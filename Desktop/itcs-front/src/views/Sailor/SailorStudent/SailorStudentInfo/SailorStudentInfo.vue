<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-33">
        <b>{{ $t('number') }}:</b>
        {{ sailorDocument.number }}
      </div>
      <div class="w-33">
        <b>{{ $t('serial') }}:</b>
        {{ sailorDocument.serial }}
      </div>
      <div
        v-if="sailorDocument.group"
        class="w-33"
      >
        <b>{{ $t('group') }}:</b>
        {{ sailorDocument.group }}
      </div>
      <div class="w-100">
        <b>{{ $t('nameInstitution') }}:</b>
        {{ sailorDocument.name_nz[labelName] }}
      </div>
      <div class="w-100">
        <b>{{ $t('way') }}:</b>
        {{ sailorDocument.faculty[labelName] }}
      </div>
      <div class="w-100">
        <b>{{ $t('educationForm') }}:</b>
        {{ sailorDocument.education_form[labelName] }}
      </div>
      <div class="w-50">
        <b>{{ $t('dataEnrollment') }}:</b>
        {{ getDateFormat(sailorDocument.date_start) }}
      </div>
      <div
        v-if="sailorDocument.date_end"
        class="w-50"
      >
        <b>{{ $t('dateEnd') }}:</b>
        {{ getDateFormat(sailorDocument.date_end) }}
      </div>
      <div class="w-100">
        <b>{{ $t('educationWithSQC') }}:</b>
        {{ sailorDocument.educ_with_dkk ? $t('yes') : $t('no') }}
      </div>
      <div class="w-100">
        <b>{{ $t('passedEducationExam') }}:</b>
        {{ sailorDocument.passed_educ_exam ? $t('yes') : $t('no') }}
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

<script src="./SailorStudentInfo.js"/>
