<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-33">
        <b>{{ $t('registrationNumber') }}:</b>
        {{ sailorDocument.registry_number }}
      </div>
      <div class="w-33">
        <b>{{ $t('number') }}:</b>
        {{ sailorDocument.number_document }}
      </div>
      <div class="w-33">
        <b>{{ $t('serial') }}:</b>
        {{ sailorDocument.serial }}
      </div>
      <div class="w-50">
        <b>{{ $t('typeDoc') }}:</b>
        {{ sailorDocument.type_document[labelName] }}
      </div>
      <div
        v-if="sailorDocument.extent"
        class="w-50"
      >
        <b>{{ $t('educationExtent') }}:</b>
        {{ sailorDocument.extent[labelName] }}
      </div>
      <div>
        <b>{{ $t('nameInstitution') }}:</b>
        {{ sailorDocument.name_nz[labelName] }}
      </div>
      <div>
        <b>{{ $t('qualification') }}:</b>
        {{ sailorDocument.qualification[labelName] }}
      </div>
      <div v-if="sailorDocument.speciality">
        <b v-if="sailorDocument.type_document.id === 1">
          {{ $t('specialty') }}:
        </b>
        <b v-if="sailorDocument.type_document.id === 2">
          {{ $t('profession') }}:
        </b>
        {{ sailorDocument.speciality[labelName] }}
      </div>
      <div v-if="sailorDocument.specialization">
        <b>{{ $t('specialization') }}:</b>
        {{ sailorDocument.specialization[labelName] }}
      </div>
      <div
        v-if="checkAccess('document-author-view') && sailorDocument.created_by"
        class="text-left p-0"
      >
        <div class="w-50">
          <b>{{ $t('recordAuthor') }}:</b>
          {{ sailorDocument.created_by.name}}
        </div>
        <div class="w-50">
          <b>{{ $t('createDate') }}:</b>
          {{ sailorDocument.created_by.date }}
        </div>
      </div>
      <div>
        <b>{{ $t('duplicate') }}:</b>
        {{ sailorDocument.is_duplicate ? $t('yes') : $t('no') }}
      </div>
      <div class="w-33">
        <b>{{ $t('dateIssue') }}:</b>
        {{ getDateFormat(sailorDocument.date_issue_document) }}
      </div>
      <div
        v-if="sailorDocument.type_document.id === 1 || sailorDocument.type_document.id === 2"
        class="w-33"
      >
        <b>{{ $t('yearEndEducation') }}:</b>
        {{ sailorDocument.date_end_educ.split('-')[0] }}
      </div>
      <div
        v-else
        class="w-33"
      >
        <b>{{ $t('dateEndEducation') }}:</b>
        {{ getDateFormat(sailorDocument.date_end_educ) }}
      </div>
      <!--если тип документа - Свидетельство про повышение квал-->
      <div
        v-if="sailorDocument.type_document.id === 3"
        class="w-33"
      >
        <b>{{ $t('dateEnd') }}:</b>
        {{ getDateFormat(sailorDocument.experied_date) }}
      </div>
      <div
        v-if="checkAccess('verification-author-view') && sailorDocument.verificated_by"
        class="text-left p-0"
      >
        <div class="w-50">
          <b>{{ $t('verifier') }}:</b>
          {{ sailorDocument.verificated_by.name }}
        </div>
        <div class="w-50">
          <b>{{ $t('verificationDate') }}:</b>
          {{ sailorDocument.verificated_by.date }}
        </div>
      </div>
      <div class="w-100">
        <b>{{ $t('notes') }}:</b>
        {{ sailorDocument.special_notes }}
      </div>
      <div class="w-100">
        <b>{{ $t('status') }}:</b>
        <span :class="getStatus(sailorDocument.status_document.id)">
          {{ sailorDocument.status_document[labelName] }}
        </span>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorEducationInfo.js"/>
