from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework import routers

from payments import views

router = routers.SimpleRouter()

urlpatterns = [
    path('statement_dkk/<int:id>/', views.SendInvoice.as_view()),
    path('success_payments_idgovua/', views.SuccessPayments.as_view()),
    path('error_payments_idgovua/', views.ErrorPayments.as_view()),
    path('redirect/', RedirectView.as_view(url='https://sea.e-transport.gov.ua/', permanent=True),
         name='payment_redirect'),
    path('check_statement_pay/<int:statement_id>/', views.CheckStatementDKKForPay.as_view()),
    path('check_statement_service_record_pay/<int:statement_id>/', views.CheckStatementServiceRecordForPay.as_view()),
    path('check_statement_qual_doc_pay/<int:statement_id>/', views.CheckStatementStatementQualDocForPay.as_view()),
    path('create_payment/', views.CreatePayment.as_view()),
    path('success_payments_api/', views.SuccessPaymentsAPI.as_view()),
    path('error_payments_api/', views.ErrorPaymentsAPI.as_view()),
    path('check_payment_document/', views.CheckPaymentDocument.as_view()),
    path('platon/', include('payments.platon.urls'))
]

urlpatterns = urlpatterns + router.urls
