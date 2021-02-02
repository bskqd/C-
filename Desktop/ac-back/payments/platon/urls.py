from django.urls import path

from payments.platon import views

urlpatterns = [
    path('receive_payment/', views.ReceivePayment.as_view()),
    path('pay_packet/<int:packet_id>/', views.SendInvoiceForPacket.as_view()),
    path('statement_sqc/<int:pk>/', views.StatementSQCPay.as_view(), name='statement-sqc-pay'),
    path('statement_dpd/<int:pk>/', views.StatementDPDPay.as_view()),
    path('statement_certificate/<int:pk>/', views.StatementCertificatesPay.as_view(), name='pay_for_certificate'),
    path('statement_sailor_passport/<int:pk>/', views.StatementSailorPassportPay.as_view()),
    path('blank_sailor_passport/<int:pk>/', views.BlankStatementSailorPassportPay.as_view()),
    path('apple_pay/receive/', views.ApplePayReceive.as_view()),
    path('packet_branch_office/<int:pk>/', views.BranchOfficePay.as_view(), name='packet-branch-office-pay'),
]
