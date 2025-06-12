from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
import csv
from .models import (
    Employee, Department, Position, Device, DeviceType, 
    DeviceAssignmentHistory
)
from .forms import (
    EmployeeForm, DeviceForm, DepartmentForm, PositionForm,
    DeviceTypeForm, DeviceAssignmentForm
)

def login_view(request):
    """Simple login view - shows login page or redirects if already authenticated"""
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')
    return render(request, 'registration/login.html')

def logout_view(request):
    """Simple logout view - shows confirmation or handles logout"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('login_view')
    return render(request, 'registration/logout.html')

def home(request):
    """Home page - redirects to login or dashboard"""
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')
    return redirect('login_view')

@login_required
def dashboard(request):
    """Main dashboard with statistics"""
    context = {
        'total_employees': Employee.objects.filter(status=1).count(),
        'total_devices': Device.objects.count(),
        'assigned_devices': Device.objects.filter(status='assigned').count(),
        'available_devices': Device.objects.filter(status='available').count(),
        'departments': Department.objects.filter(status=1).count(),
        'recent_assignments': DeviceAssignmentHistory.objects.filter(
            returned_date__isnull=True
        ).select_related('device', 'employee', 'device__device_type', 'employee__department').order_by('-assigned_date')[:5],
        'device_types': DeviceType.objects.filter(status=1).annotate(
            device_count=Count('devices')
        ),
    }
    return render(request, 'inventory/dashboard.html', context)

@login_required
def employee_list(request):
    """List all employees with search and filter"""
    query = request.GET.get('q')
    department = request.GET.get('department')
    
    # Annotate with assigned device count using a different name
    employees = Employee.objects.filter(status=1).annotate(
        device_count=Count('devices', filter=Q(devices__status='assigned'))
    ).select_related('department', 'position')
    
    # Add the count as assigned_device_count attribute for template compatibility
    for emp in employees:
        emp.assigned_device_count = emp.device_count
    
    if query:
        employees = employees.filter(
            Q(firstname__icontains=query) |
            Q(lastname__icontains=query) |
            Q(email__icontains=query) |
            Q(code__icontains=query)
        )
    
    if department:
        employees = employees.filter(department_id=department)
    
    context = {
        'employees': employees,
        'departments': Department.objects.filter(status=1),
    }
    return render(request, 'inventory/employees_list.html', context)

@login_required
def employee_detail(request, pk):
    """Employee detail view with proper device relationships"""
    employee = get_object_or_404(Employee, pk=pk)
    
    # Get currently assigned devices
    assigned_devices = Device.objects.filter(
        assigned_to=employee,
        status='assigned'
    ).select_related('device_type')
    
    # Get all device assignment history for this employee
    device_history = DeviceAssignmentHistory.objects.filter(
        employee=employee
    ).select_related('device', 'device__device_type').order_by('-assigned_date')
    
    context = {
        'employee': employee,
        'assigned_devices': assigned_devices,
        'assigned_devices_count': assigned_devices.count(),
        'device_history': device_history,
    }
    return render(request, 'inventory/employee_detail.html', context)

@login_required
def employee_add(request):
    """Add new employee"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.full_name} added successfully!')
            return redirect('inventory:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm()
    
    return render(request, 'inventory/employee_form.html', {
        'form': form,
        'title': 'Add New Employee'
    })

@login_required
def employee_edit(request, pk):
    """Edit employee"""
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('inventory:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'inventory/employee_form.html', {
        'form': form,
        'title': 'Edit Employee',
        'employee': employee
    })

@login_required
def employee_delete(request, pk):
    """Delete employee (soft delete)"""
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.status = 0
        employee.save()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('inventory:employee_list')
    
    return render(request, 'inventory/confirm_delete.html', {
        'object': employee,
        'type': 'Employee'
    })

@login_required
def device_list(request):
    """List all devices with filters"""
    query = request.GET.get('q')
    device_type = request.GET.get('type')
    status = request.GET.get('status')
    
    devices = Device.objects.select_related('device_type', 'assigned_to', 'assigned_to__department')
    
    if query:
        devices = devices.filter(
            Q(serial_number__icontains=query) |
            Q(brand__icontains=query) |
            Q(model__icontains=query)
        )
    
    if device_type:
        devices = devices.filter(device_type_id=device_type)
    
    if status:
        devices = devices.filter(status=status)
    
    context = {
        'devices': devices,
        'device_types': DeviceType.objects.filter(status=1),
        'statuses': Device.STATUS_CHOICES,
    }
    return render(request, 'inventory/devices_list.html', context)

@login_required
def device_detail(request, pk):
    """Device detail view"""
    device = get_object_or_404(Device, pk=pk)
    assignment_history = device.assignment_history.select_related('employee').order_by('-assigned_date')
    
    context = {
        'device': device,
        'assignment_history': assignment_history,
    }
    return render(request, 'inventory/device_detail.html', context)

@login_required
def device_add(request):
    """Add new device"""
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            
            # If device is assigned during creation, create assignment history
            if device.assigned_to:
                device.status = 'assigned'
                if not device.date_assigned:
                    device.date_assigned = timezone.now().date()
            
            device.save()
            
            # Create assignment history if assigned
            if device.assigned_to:
                DeviceAssignmentHistory.objects.create(
                    device=device,
                    employee=device.assigned_to,
                    assigned_date=device.date_assigned,
                    reason='Assigned during device creation',
                    assigned_by=request.user.get_full_name() or request.user.username
                )
            
            messages.success(request, f'Device {device.serial_number} added successfully!')
            return redirect('inventory:device_detail', pk=device.pk)
    else:
        form = DeviceForm()
    
    return render(request, 'inventory/device_form.html', {
        'form': form,
        'title': 'Add New Device'
    })

@login_required
def device_edit(request, pk):
    """Edit device"""
    device = get_object_or_404(Device, pk=pk)
    old_assignee = device.assigned_to
    
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            updated_device = form.save(commit=False)
            
            # Check if assignment changed
            if old_assignee != updated_device.assigned_to:
                if old_assignee and not updated_device.assigned_to:
                    # Device was returned
                    # Update old assignment history
                    old_assignment = DeviceAssignmentHistory.objects.filter(
                        device=device,
                        employee=old_assignee,
                        returned_date__isnull=True
                    ).first()
                    if old_assignment:
                        old_assignment.returned_date = timezone.now().date()
                        old_assignment.save()
                    
                    updated_device.status = 'available'
                    updated_device.date_assigned = None
                    
                elif updated_device.assigned_to:
                    # Device was assigned or reassigned
                    if old_assignee:
                        # Mark old assignment as returned
                        old_assignment = DeviceAssignmentHistory.objects.filter(
                            device=device,
                            employee=old_assignee,
                            returned_date__isnull=True
                        ).first()
                        if old_assignment:
                            old_assignment.returned_date = timezone.now().date()
                            old_assignment.save()
                    
                    # Create new assignment history
                    updated_device.status = 'assigned'
                    updated_device.date_assigned = timezone.now().date()
                    
                    updated_device.save()
                    
                    DeviceAssignmentHistory.objects.create(
                        device=updated_device,
                        employee=updated_device.assigned_to,
                        assigned_date=updated_device.date_assigned,
                        reason='Assigned during device edit',
                        assigned_by=request.user.get_full_name() or request.user.username
                    )
                else:
                    updated_device.save()
            else:
                updated_device.save()
            
            messages.success(request, 'Device updated successfully!')
            return redirect('inventory:device_detail', pk=device.pk)
    else:
        form = DeviceForm(instance=device)
    
    return render(request, 'inventory/device_form.html', {
        'form': form,
        'title': 'Edit Device',
        'device': device
    })

@login_required
def device_delete(request, pk):
    """Delete device"""
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        device.delete()
        messages.success(request, 'Device deleted successfully!')
        return redirect('inventory:device_list')
    
    return render(request, 'inventory/confirm_delete.html', {
        'object': device,
        'type': 'Device'
    })

@login_required
def device_assign(request, pk):
    """Assign device to employee"""
    device = get_object_or_404(Device, pk=pk)
    
    if device.status != 'available':
        messages.error(request, 'This device is not available for assignment.')
        return redirect('inventory:device_detail', pk=device.pk)
    
    if request.method == 'POST':
        form = DeviceAssignmentForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            reason = form.cleaned_data.get('reason', '')
            
            # Update device
            device.assigned_to = employee
            device.status = 'assigned'
            device.date_assigned = timezone.now().date()
            device.save()
            
            # Create assignment history
            DeviceAssignmentHistory.objects.create(
                device=device,
                employee=employee,
                assigned_date=timezone.now().date(),
                assigned_by=request.user.get_full_name() or request.user.username,
                reason=reason
            )
            
            messages.success(request, f'Device assigned to {employee.full_name} successfully!')
            return redirect('inventory:device_detail', pk=device.pk)
    else:
        form = DeviceAssignmentForm()
    
    return render(request, 'inventory/device_assign.html', {
        'form': form,
        'device': device
    })

@login_required
def device_return(request, pk):
    """Return device from employee"""
    device = get_object_or_404(Device, pk=pk)
    
    if device.status != 'assigned' or not device.assigned_to:
        messages.error(request, 'This device is not currently assigned.')
        return redirect('inventory:device_detail', pk=device.pk)
    
    if request.method == 'POST':
        # Update assignment history first
        current_assignment = DeviceAssignmentHistory.objects.filter(
            device=device,
            employee=device.assigned_to,
            returned_date__isnull=True
        ).first()
        
        if current_assignment:
            current_assignment.returned_date = timezone.now().date()
            current_assignment.save()
        
        # Update device
        device.assigned_to = None
        device.status = 'available'
        device.date_assigned = None
        device.save()
        
        messages.success(request, 'Device returned successfully!')
        return redirect('inventory:device_detail', pk=device.pk)
    
    return render(request, 'inventory/device_return.html', {
        'device': device
    })

@login_required
def department_list(request):
    """List all departments"""
    departments = Department.objects.filter(status=1).annotate(
        emp_count=Count('employees', filter=Q(employees__status=1))
    )
    # Add the employee count as a separate attribute to avoid template issues
    for dept in departments:
        dept.employee_count = dept.emp_count
    
    return render(request, 'inventory/department_list.html', {
        'departments': departments
    })

@login_required
def department_add(request):
    """Add new department"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, 'Department added successfully!')
            return redirect('inventory:department_list')
    else:
        form = DepartmentForm()
    
    return render(request, 'inventory/form.html', {
        'form': form,
        'title': 'Add New Department'
    })

@login_required
def department_edit(request, pk):
    """Edit department"""
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('inventory:department_list')
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'inventory/form.html', {
        'form': form,
        'title': 'Edit Department'
    })

@login_required
def department_delete(request, pk):
    """Delete department (soft delete)"""
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        # Check if department has employees
        if department.employees.filter(status=1).exists():
            messages.error(request, 'Cannot delete department with active employees. Please reassign employees first.')
            return redirect('inventory:department_list')
        
        # Soft delete - set status to 0
        department.status = 0
        department.save()
        messages.success(request, f'Department "{department.name}" deleted successfully!')
        return redirect('inventory:department_list')
    
    return render(request, 'inventory/confirm_delete.html', {
        'object': department,
        'type': 'Department'
    })

@login_required
def position_list(request):
    """List all positions"""
    positions = Position.objects.filter(status=1).annotate(
        emp_count=Count('employees', filter=Q(employees__status=1))
    )
    # Add the employee count as a separate attribute to avoid template issues
    for pos in positions:
        pos.employee_count = pos.emp_count
    
    return render(request, 'inventory/position_list.html', {
        'positions': positions
    })

@login_required
def position_add(request):
    """Add new position"""
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save()
            messages.success(request, 'Position added successfully!')
            return redirect('inventory:position_list')
    else:
        form = PositionForm()
    
    return render(request, 'inventory/form.html', {
        'form': form,
        'title': 'Add New Position'
    })

@login_required
def position_edit(request, pk):
    """Edit position"""
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, 'Position updated successfully!')
            return redirect('inventory:position_list')
    else:
        form = PositionForm(instance=position)
    
    return render(request, 'inventory/form.html', {
        'form': form,
        'title': 'Edit Position'
    })

@login_required
def position_delete(request, pk):
    """Delete position (soft delete)"""
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        # Check if position has employees
        if position.employees.filter(status=1).exists():
            messages.error(request, 'Cannot delete position with active employees. Please reassign employees first.')
            return redirect('inventory:position_list')
        
        # Soft delete - set status to 0
        position.status = 0
        position.save()
        messages.success(request, f'Position "{position.name}" deleted successfully!')
        return redirect('inventory:position_list')
    
    return render(request, 'inventory/confirm_delete.html', {
        'object': position,
        'type': 'Position'
    })

@login_required
def reports(request):
    """Reports dashboard"""
    total_employees = Employee.objects.filter(status=1).count()
    total_devices = Device.objects.count()
    assigned_devices = Device.objects.filter(status='assigned').count()
    available_devices = Device.objects.filter(status='available').count()

    # Compute average devices per employee
    if total_employees > 0:
        avg_devices_per_employee = round(assigned_devices / total_employees, 2)
    else:
        avg_devices_per_employee = 0

    context = {
        'total_employees': total_employees,
        'total_devices': total_devices,
        'assigned_devices': assigned_devices,
        'available_devices': available_devices,
        'avg_devices_per_employee': avg_devices_per_employee,
        'device_by_status': Device.objects.values('status').annotate(count=Count('id')),
        'device_by_type': DeviceType.objects.annotate(count=Count('devices')),
        'assignments_by_month': DeviceAssignmentHistory.objects.extra(
            select={'month': "strftime('%%Y-%%m', assigned_date)"}
        ).values('month').annotate(count=Count('id')).order_by('-month')[:12],
    }
    return render(request, 'inventory/reports.html', context)

@login_required
def export_report(request):
    """Export report as CSV"""
    report_type = request.GET.get('type', 'devices')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    
    if report_type == 'devices':
        writer.writerow(['Serial Number', 'Type', 'Brand', 'Model', 'Status', 'Assigned To', 'Department', 'Date Assigned'])
        devices = Device.objects.select_related('device_type', 'assigned_to', 'assigned_to__department')
        for device in devices:
            writer.writerow([
                device.serial_number,
                device.device_type.name if device.device_type else 'Unknown',
                device.brand or '',
                device.model or '',
                device.get_status_display(),
                device.assigned_to.full_name if device.assigned_to else 'Unassigned',
                device.assigned_to.department.name if device.assigned_to else '',
                device.date_assigned or ''
            ])
    
    elif report_type == 'employees':
        writer.writerow(['Code', 'Name', 'Email', 'Department', 'Position', 'Assigned Devices'])
        employees = Employee.objects.filter(status=1).select_related('department', 'position').prefetch_related('devices')
        for employee in employees:
            assigned_devices = employee.devices.filter(status='assigned')
            device_list = ', '.join([f"{d.device_type.name if d.device_type else 'Unknown'} ({d.serial_number})" for d in assigned_devices])
            writer.writerow([
                employee.code,
                employee.full_name,
                employee.email,
                employee.department.name,
                employee.position.name,
                device_list or 'No devices assigned'
            ])
    
    return response