from django.contrib import admin
from .models import (
    Department, Position, Employee, DeviceType, 
    Device, DeviceAssignmentHistory
)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'date_added', 'date_updated']
    list_filter = ['status', 'date_added']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'date_added', 'date_updated']
    list_filter = ['status', 'date_added']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['code', 'full_name', 'email', 'department', 'position', 'status']
    list_filter = ['status', 'department', 'position', 'gender']
    search_fields = ['code', 'firstname', 'lastname', 'email']
    ordering = ['firstname', 'lastname']
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Name'

@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'date_added']
    list_filter = ['status']
    search_fields = ['name']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'device_type', 'brand', 'model', 
                   'status', 'assigned_to', 'date_assigned']
    list_filter = ['status', 'device_type', 'date_assigned']
    search_fields = ['serial_number', 'brand', 'model']
    raw_id_fields = ['assigned_to']
    date_hierarchy = 'date_assigned'

@admin.register(DeviceAssignmentHistory)
class DeviceAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ['device', 'employee', 'assigned_date', 
                   'returned_date', 'assigned_by']
    list_filter = ['assigned_date', 'returned_date']
    search_fields = ['device__serial_number', 'employee__firstname', 
                    'employee__lastname']
    date_hierarchy = 'assigned_date'