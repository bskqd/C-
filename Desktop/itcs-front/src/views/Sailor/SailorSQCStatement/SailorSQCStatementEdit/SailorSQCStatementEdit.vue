<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div>
        <div>
          {{ $t('dataEvent') }}
        </div>
        <b-input-group>
          <b-form-input
            v-model="sailorDocument.date_meeting"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="sailorDocument.date_meeting"
              :locale="lang"
              :date-disabled-fn="(ymd, date) => dateDisabled(ymd, date, sailorDocument)"
              :min="new Date()"
              start-weekday="1"
              button-only
              right
            />
          </b-input-group-append>
        </b-input-group>
      </div>
      <div>
        <FileDropZone ref="mediaContent" class="w-100 p-0" />
      </div>
      <div class="text-center">
        <b-overlay
          :show="buttonLoader"
          spinner-variant="primary"
          opacity="0.65"
          blur="2px"
          variant="white"
          class="w-100"
          spinner-small
        >
          <b-button
            @click="saveEditedApplication()"
            class="mt-1"
            variant="success"
          >
            {{ $t('save') }}
          </b-button>
        </b-overlay>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorSQCStatementEdit.js"></script>
