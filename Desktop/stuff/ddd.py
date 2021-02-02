        if statement_dkk.is_continue == 1:
            diploma = QualificationDocument.objects.filter(rank=statement_dkk.rank,
                                                           list_positions=statement_dkk.list_positions) \
                .latest('date_start')
            if diploma.type_document_id != 49:
                function_limitation = diploma.function_limitation
            else:
                function_limitation = ProofOfWorkDiploma.objects.filter(diploma=diploma).latest('date_start') \
                    .function_limitation
        date_meeting = datetime.strptime(serializer.initial_data['date_meeting'], '%Y-%m-%d')
        date_end = (date_meeting + relativedelta(years=1)).strftime('%Y-%m-%d')
        ser = serializer.save(branch_create_id=author.userprofile.branch_office_id, author=author,
                              number_document=number, status_document_id=29, _sailor=sailor_id, date_end=date_end,
                              is_printeble=is_printable, function_limitation=function_limitation)
        if ser.statement_dkk.related_docs.exists():
            ser.related_docs = list(ser.statement_dkk.related_docs.all())
        else:
            docs_set = ser.statement_dkk.get_status_position
        if sailor_qs.protocol_dkk:
            sailor_qs.protocol_dkk.append(ser.id)
            sailor_qs.save(update_fields=['protocol_dkk'])
        else:
            sailor_qs.protocol_dkk = [ser.id]
            sailor_qs.save(update_fields=['protocol_dkk'])
        sailor.tasks.save_history.s(user_id=self.request.user.id, module='ProtocolDKK', action_type='create',
                                    content_obj=ser, serializer=sailor.document.serializers.ProtocolDKKSerializer,
                                    new_obj=ser,
                                    sailor_key_id=sailor_id).apply_async(serializer='pickle')
        if ser.decision_id == magic_numbers.decision_allow:
            update_protocol_in_packet.delay(ser.pk, sailor_id)

    def perform_destroy(self, instance):
        if hasattr(instance, 'statementqualification'):
            raise ValidationError('This protocol has a statement qual doc')
        return super(ProtocolSQCView, self).perform_destroy(instance=instance)

    @action(detail=False, methods=['get'])
    def success(self, request, sailor_pk, *args, **kwargs):
        try:
            keys = SailorKeys.objects.get(id=sailor_pk)
        except (SailorKeys.DoesNotExist, KeyError):
            raise ValidationError(sailor_not_exists_error)
        queryset = self.get_queryset()
        quals_docs = QualificationDocument.objects.filter(id__in=keys.qualification_documents)
        proofs_docs = ProofOfWorkDiploma.objects.filter(diploma__in=quals_docs)
        exclude_list = []
        protocols = queryset.filter(
            Q(statementqualification__isnull=True)
            & Q(status_document_id=magic_numbers.status_protocol_dkk_valid)
            & Q(decision_id=magic_numbers.decision_allow) & Q(is_printeble=True)).order_by('-id')
        for protocol in protocols:
            qual_doc = quals_docs.filter(rank_id=protocol.statement_dkk.rank_id,
                                         list_positions__contains=protocol.statement_dkk.list_positions,
                                         date_start__gte=protocol.date_meeting)
            proof_doc = proofs_docs.filter(diploma__rank_id=protocol.statement_dkk.rank_id,
                                           diploma__list_positions__contains=protocol.statement_dkk.list_positions,
                                           date_start__gte=protocol.date_meeting)
            if proof_doc.exists() or qual_doc.exists():
                exclude_list.append(protocol.pk)
        protocols = protocols.exclude(id__in=exclude_list)
        return Response(self.special_serializer_class(protocols, many=True).data)


class CertificateETIView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        sailor.document.permissions.CertificatesStatusPermission,
    )
    queryset = CertificateETI.objects.all()
    serializer_class = sailor.document.serializers.CertificateNTZSerializer
    model = CertificateETI
    select_related = ('ntz', 'course_training', 'status_document',)
    prefetch_related = ('items',)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(ntz_number=-1)

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        statement: StatementETI = serializer.validated_data.get('statement')
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        if statement:
            statement.status_document_id = StatementETI.StatusDocument.CERTIFICATE_CREATED
            statement.save(update_fields=['status_document'])
        ser = serializer.save(is_red=serializer.validated_data.get('ntz').is_red)
        sailor_qs.sertificate_ntz.append(ser.id)
        sailor_qs.save(update_fields=['sertificate_ntz'])
        sailor.tasks.save_history.s(user_id=self.request.user.id, module='CertificateNTZ', action_type='create',
                                    content_obj=ser, serializer=sailor.document.serializers.CertificateNTZSerializer,
                                    new_obj=ser,
                                    sailor_key_id=sailor_id).apply_async(serializer='pickle')
        if ser.status_document_id in magic_numbers.ALL_VALID_STATUSES:
            update_eti_in_packet.delay(ser.pk, sailor_id)


class MedicalCertificateView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        (sailor.document.permissions.MedicalCertificatePermission |
         sailor.permissions.PostVerificationChangeStatusPermission)
    )
    queryset = MedicalCertificate.objects.all()
    serializer_class = sailor.document.serializers.MedicalCertificateSerializer
    model = MedicalCertificate
    select_related = ('position', 'limitation', 'doctor', 'status_document', 'medical_statement')

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=int(sailor_id))
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        status_document_id = self.request.user.userprofile.verification_status_by_user
        doctor = serializer.validated_data.get('doctor')
        if self.request.user.userprofile.type_user == self.request.user.userprofile.MEDICAL:
            doctor = self.request.user.userprofile.doctor_info
        ser = serializer.save(status_document_id=status_document_id, author=self.request.user, doctor=doctor)
        if ser.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(ser)
        sailor_qs.medical_sertificate.append(ser.id)
        sailor_qs.save(update_fields=['medical_sertificate'])
        sailor.tasks.save_history.s(user_id=self.request.user.id, module='MedicalCertificate', action_type='create',
                                    content_obj=ser,
                                    serializer=sailor.document.serializers.MedicalCertificateSerializer,
                                    new_obj=ser,
                                    sailor_key_id=sailor_id).apply_async(serializer='pickle')

    def get_queryset(self):
        qs: QuerySet[MedicalCertificate] = super().get_queryset()
        up: UserProfile = self.request.user.userprofile
        if up.type_user in [up.MEDICAL]:
            return qs.filter(status_document_id=magic_numbers.status_qual_doc_valid)
        elif up.type_user in [up.VERIFIER, up.SECRETARY_SQC, up.MARAD, up.ETI_EMPLOYEE]:
            qs = qs.exclude(status_document_id=magic_numbers.STATUS_CREATED_BY_AGENT)
        return qs


class QualificationDocumentView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        (sailor.document.permissions.QualificationStatusPermission |
         sailor.permissions.PostVerificationChangeStatusPermission)
    )
    queryset = QualificationDocument.objects.all()
    serializer_class = sailor.document.serializers.QualificationDocumentSerializer
    model = QualificationDocument
    select_related = ('country', 'rank', 'type_document', 'status_document', 'statement', 'port')
    prefetch_related = ('related_docs', 'verification_status', 'items')

    def raise_on_early_non_agent_statement(self, statement: StatementQualification):
        today = date.today()
        created_at = statement.created_at
        td = today - created_at.date()
        if not statement.items.exists() and td.days < 13 and not self.request.user.is_superuser:
            raise ValidationError('Early for create this qualification document')

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        new_document = serializer.initial_data.get('new_document')
        date_end = serializer.initial_data.get('date_end', None)
        function_limitation = serializer.initial_data.get('function_limitation')
        if new_document:
            statement_instance = serializer.validated_data.get('statement')
            date_start = date.today()
            if (QualificationDocument.objects.filter(statement=statement_instance
                                                     ).exclude(status_document_id=17).exists() or
                    ProofOfWorkDiploma.objects.filter(statement=statement_instance
                                                      ).exclude(status_document_id=17).exists()):
                raise ValidationError('Qualification document with this statement exists')
            self.raise_on_early_non_agent_statement(statement=statement_instance)
            if QualificationDocument.objects.filter(rank=statement_instance.rank,
                                                    list_positions=statement_instance.list_positions).exists():
                previous_diploma = QualificationDocument.objects.filter(rank=statement_instance.rank,
                                                                        list_positions=statement_instance.list_positions) \
                    .latest('date_start')
                function_limitation = previous_diploma.function_limitation