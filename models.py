from datetime import datetime
from django.db import models
from django.utils import timezone

# Department model
class Department(models.Model):
    name = models.TextField()
    description = models.TextField()
    status = models.IntegerField(default=1, help_text="1=Active, 0=Inactive")
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_employee_count(self):
        return self.employees.filter(status=1).count()

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']


# Position model
class Position(models.Model):
    name = models.TextField()
    description = models.TextField()
    status = models.IntegerField(default=1, help_text="1=Active, 0=Inactive")
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_employee_count(self):
        return self.employees.filter(status=1).count()

    class Meta:
        verbose_name = "Position"
        verbose_name_plural = "Positions"
        ordering = ['name']


# Employee model
class Employee(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    code = models.CharField(max_length=100, blank=True, unique=True, help_text="Employee ID/Code")
    firstname = models.TextField(verbose_name="First Name")
    middlename = models.TextField(blank=True, null=True, verbose_name="Middle Name")
    lastname = models.TextField(verbose_name="Last Name")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField()
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='employees')
    status = models.IntegerField(default=1, help_text="1=Active, 0=Inactive")
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.firstname} {self.middlename or ''} {self.lastname}".strip()

    @property
    def full_name(self):
        return f"{self.firstname} {self.middlename or ''} {self.lastname}".strip()
    
    def get_assigned_device_count(self):
        return self.devices.filter(status='assigned').count()
    
    def get_assigned_devices(self):
        return self.devices.filter(status='assigned')
    
    def get_device_history(self):
        return self.device_history.all().order_by('-assigned_date')

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ['firstname', 'lastname']


# Device Type model
class DeviceType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(default=1, help_text="1=Active, 0=Inactive")
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_device_count(self):
        return self.devices.count()

    class Meta:
        verbose_name = "Device Type"
        verbose_name_plural = "Device Types"
        ordering = ['name']


# Device model
class Device(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    ]

    serial_number = models.CharField(max_length=100, unique=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, related_name='devices', null=True, blank=True)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='devices', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    remark = models.TextField(blank=True, null=True)
    date_assigned = models.DateField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.device_type:
            device_name = f"{self.brand} {self.model}" if self.brand or self.model else self.device_type.name
        else:
            device_name = f"{self.brand} {self.model}" if self.brand or self.model else "Unknown Device"
        assigned_info = f" - {self.assigned_to}" if self.assigned_to else " - Unassigned"
        return f"{device_name} ({self.serial_number}){assigned_info}"

    @property
    def is_assigned(self):
        return self.assigned_to is not None

    def save(self, *args, **kwargs):
        # Update date_assigned when device is assigned
        if self.assigned_to and not self.date_assigned:
            self.date_assigned = timezone.now().date()
        elif not self.assigned_to:
            self.date_assigned = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"
        ordering = ['-date_updated', 'serial_number']


# Device Assignment History
class DeviceAssignmentHistory(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='assignment_history')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='device_history')
    assigned_date = models.DateField()
    returned_date = models.DateField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    assigned_by = models.CharField(max_length=100, blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        status = "Active" if not self.returned_date else f"Returned on {self.returned_date}"
        return f"{self.device.serial_number} - {self.employee.full_name} ({status})"

    class Meta:
        verbose_name = "Device Assignment History"
        verbose_name_plural = "Device Assignment Histories"
        ordering = ['-assigned_date']