from django.urls import path

import document_generation.views

urlpatterns = [
    path('io_request/<int:request_id>/', document_generation.views.GeneratePortClearanceView.as_view()),
    path('io_request/with_watermark/<int:document_id>/',
         document_generation.views.DownloadIORequestWatermarkView.as_view()),
    path('io_request/archive/<int:document_id>/', document_generation.views.DownloadIORequestArchiveView.as_view()),
    path('photo/archive/<int:pk>/', document_generation.views.DownloadPhotoArchiveView.as_view())
]
