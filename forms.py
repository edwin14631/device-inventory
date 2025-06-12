from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Employee, Department, Position, Device, DeviceType, 
    DeviceAssignmentHistory
)

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['code', 'firstname', 'middlename', 'lastname', 
                 'gender', 'address', 'email', 'department', 'position']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['gender', 'department', 'position']:
                self.fields[field].widget.attrs['class'] = 'form-control'

class DeviceForm(forms.ModelForm):
    # Define the device type choices
    DEVICE_TYPE_CHOICES = [
        ('', '--- Select Device Type ---'),
        ('laptop', 'Laptop'),
        ('monitor_1', 'Monitor - 1'),
        ('monitor_2', 'Monitor - 2'),
        ('mouse_1', 'Mouse - 1'),
        ('mouse_2', 'Mouse - 2'),
        ('keyboard', 'Keyboard'),
        ('headset', 'Headset'),
        ('smartphone_1', 'Smart Phone - 1'),
        ('smartphone_2', 'Smart Phone - 2'),
        ('remarkable', 'Remarkable'),
    ]
    
    # Add a custom choice field for device type selection
    device_type_choice = forms.ChoiceField(
        choices=DEVICE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Device Type',
        required=True
    )
    
    # Add employee assignment field
    assigned_to = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status=1),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Assign to Employee',
        required=False,
        empty_label='--- Not Assigned ---'
    )
    
    class Meta:
        model = Device
        fields = ['serial_number', 'brand', 'model', 'status', 'assigned_to', 'remark']
        widgets = {
            'remark': forms.Textarea(attrs={'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Style the form fields
        for field in self.fields:
            if field not in ['status', 'assigned_to', 'device_type_choice']:
                self.fields[field].widget.attrs['class'] = 'form-control'
        
        # Customize the employee dropdown to show more info
        self.fields['assigned_to'].label_from_instance = self.label_from_instance
        
        # If editing an existing device, set the dropdown value based on device_type name
        if self.instance and self.instance.pk and hasattr(self.instance, 'device_type') and self.instance.device_type:
            device_type_name = self.instance.device_type.name.lower().strip()
            
            # Map existing device types to new choices
            type_mapping = {
                'laptop': 'laptop',
                'monitor - 1': 'monitor_1',
                'monitor - 2': 'monitor_2',
                'monitor': 'monitor_1',  # Default to monitor_1 for generic "monitor"
                'mouse - 1': 'mouse_1',
                'mouse - 2': 'mouse_2',
                'mouse': 'mouse_1',      # Default to mouse_1 for generic "mouse"
                'keyboard': 'keyboard',
                'headset': 'headset',
                'smart phone - 1': 'smartphone_1',
                'smart phone - 2': 'smartphone_2',
                'smartphone': 'smartphone_1',
                'smart phone': 'smartphone_1',
                'phone': 'smartphone_1',
                'remarkable': 'remarkable',
            }
            
            mapped_type = type_mapping.get(device_type_name, '')
            if mapped_type:
                self.fields['device_type_choice'].initial = mapped_type
    
    def label_from_instance(self, obj):
        """Custom label for employee dropdown"""
        return f"{obj.full_name} - {obj.department.name} ({obj.code})"

    def clean_device_type_choice(self):
        """Validate device type choice"""
        device_type_choice = self.cleaned_data.get('device_type_choice')
        if not device_type_choice:
            raise forms.ValidationError("Please select a device type.")
        return device_type_choice
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        assigned_to = cleaned_data.get('assigned_to')
        
        # If device is assigned to someone, status should be 'assigned'
        if assigned_to and status != 'assigned':
            cleaned_data['status'] = 'assigned'
        
        # If device is not assigned to anyone, it cannot have status 'assigned'
        if not assigned_to and status == 'assigned':
            raise forms.ValidationError("Cannot set status to 'assigned' without assigning to an employee.")
        
        return cleaned_data

    def save(self, commit=True):
        """Override save to handle device type creation and assignment history"""
        device = super().save(commit=False)
        
        # Get the selected device type from dropdown
        selected_type = self.cleaned_data.get('device_type_choice')
        
        # Map the selected choice back to a display name and create/get DeviceType object
        if selected_type:
            device_type_name = dict(self.DEVICE_TYPE_CHOICES).get(selected_type, '')
            if device_type_name:
                device_type, created = DeviceType.objects.get_or_create(
                    name=device_type_name,
                    defaults={
                        'description': f'Auto-created device type for {device_type_name}', 
                        'status': 1
                    }
                )
                device.device_type = device_type
        
        # Handle assignment
        if device.assigned_to:
            device.status = 'assigned'
            if not device.date_assigned:
                from django.utils import timezone
                device.date_assigned = timezone.now().date()
        
        if commit:
            device.save()
            
            # Create assignment history if device is assigned
            if device.assigned_to and not self.instance.pk:  # Only for new devices
                from django.utils import timezone
                DeviceAssignmentHistory.objects.create(
                    device=device,
                    employee=device.assigned_to,
                    assigned_date=device.date_assigned or timezone.now().date(),
                    reason='Device assigned during creation',
                    assigned_by='System'
                )
        
        return device

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class DeviceTypeForm(forms.ModelForm):
    class Meta:
        model = DeviceType
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class DeviceAssignmentForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status=1),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Assign to Employee'
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        label='Assignment Reason/Notes'
    )