from docxtpl import DocxTemplate
import os
from django.conf import settings


class GenerateDocument:
    def __init__(self):
        self.type = type

    def generate_deaplom(self):
        doc = DocxTemplate(settings.BASE_DIR + '/docs/docs_file/deaplom.docx')
        context = {'name_rank':'Названия ранга', 'num_of_doc': 52, 'date_birdth': '05-02-1998',
                   'title_certificate': 'Название сертификата', 'num_sert': 55}
        return 'ok'
        doc.render(context=context)
        doc.save('generated_deaplom.docx')
