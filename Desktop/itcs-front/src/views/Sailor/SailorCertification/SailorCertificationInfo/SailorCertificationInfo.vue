<template>
  <b-card
    header-tag="header"
  >
    <div class="seafarerInfoList">
      <div>
        <b>{{ $t('number') }}:</b>
        <span>{{ sailorDocument.ntz_number }}</span>
      </div>
      <div>
        <b>{{ $t('qualification') }}:</b>
        <span >{{ sailorDocument.course_traning[labelName] }}</span>
      </div>
      <div>
        <b>{{ $t('nameInstitution') }}:</b>
        <span>{{ sailorDocument.ntz[labelName] }}</span>
      </div>
      <div>
        <b>{{ $t('dateIssue') }}:</b>
        <span>{{ getDateFormat(sailorDocument.date_start) }}</span>
      </div>
      <div>
        <b>{{ $t('dateEnd') }}:</b>
        <span>{{ getDateFormat(sailorDocument.date_end) }}</span>
      </div>
      <div v-if="checkAccess('backOffice')">
        <b>{{ $t('onlyForDPD') }}:</b>
        <span>{{ sailorDocument.is_only_dpd ? $t('yes') : $t('no') }}</span>
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

<script src="./SailorCertificationInfo.js"/>
