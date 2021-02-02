<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList text-left">
      <div>
        <b>{{ $t('number') }}:</b>
        {{ sailorDocument.number }}
      </div>
      <div>
        <b>{{ $t('medicalInstitution') }}:</b>
        {{ sailorDocument.doctor.medical_institution.value }}
      </div>
      <div>
        <b>{{ $t('doctor') }}:</b>
        {{ sailorDocument.doctor.FIO }}
      </div>
      <div class="w-50">
        <b>{{ $t('dateIssue') }}:</b>
        {{ getDateFormat(sailorDocument.date_start) }}
      </div>
      <div class="w-50">
        <b>{{ $t('dateEnd') }}:</b>
        {{ getDateFormat(sailorDocument.date_end) }}
      </div>
      <div>
        <b>{{ $t('position') }}:</b>
        {{ sailorDocument.position[labelName] }}
      </div>
      <div>
        <b>{{ $t('limitation') }}:</b>
        {{ sailorDocument.limitation[labelName] }}
      </div>
      <div
        v-if="checkAccess('document-author-view') && sailorDocument.created_by"
        class="w-50"
      >
        <b>{{ $t('recordAuthor') }}:</b>
        {{ sailorDocument.created_by.name }}
      </div>
      <div
        v-if="checkAccess('document-author-view') && sailorDocument.created_by"
        class="w-50"
      >
        <b>{{ $t('createDate') }}:</b>
        {{ sailorDocument.created_by.date }}
      </div>
      <div
        v-if="checkAccess('verification-author-view') && sailorDocument.verificated_by"
        class="w-50"
      >
        <b>{{ $t('verifier') }}:</b>
        {{ sailorDocument.verificated_by.name }}
      </div>
      <div
        v-if="checkAccess('verification-author-view') && sailorDocument.verificated_by"
        class="w-50"
      >
        <b>{{ $t('verificationDate') }}:</b>
        {{ sailorDocument.verificated_by.date }}
      </div>
      <div>
        <b>{{ $t('status') }}:</b>
        <span :class="getStatus(sailorDocument.status_document.id)">
          {{ sailorDocument.status_document[labelName] }}
        </span>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorMedicalInfo.js"/>
