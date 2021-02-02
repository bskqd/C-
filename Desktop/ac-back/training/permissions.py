from ipaddress import ip_address

from rest_framework import permissions

from personal_cabinet.utils import get_client_ip


class CreateProtocolSQCPermission(permissions.BasePermission):
    # право на создание протокола ДКК
    def has_permission(self, request, view):
        if request.method in ['POST']:
            return request.user.has_perm('sailor.createProtocolSQCTraining')
        return False


class ListApplicationsSQCPermission(permissions.BasePermission):
    # право на получение заявлений ДКК
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.has_perm('sailor.readApplicationSQCTraining')
        if request.method in ['PATCH']:
            return request.user.has_perm('sailor.writeApplicationSQCTraining')
        return False


class CheckIPAddressAST(permissions.BasePermission):
    def has_permission(self, request, view):
        addr = get_client_ip(request)
        print(addr)
        l_ip_address = map(ip_address, ['212.8.50.254', '192.168.99.7', '94.131.243.210', '10.64.10.48', '93.170.1.9'])
        return ip_address(addr) in l_ip_address


