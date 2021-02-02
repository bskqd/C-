<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-50">
        <b>{{ $t('number') }}:</b>
        <span class="required-field-star">*</span>
        <b-input
          v-model="sailorDocument.number_document"
          @blur="$v.sailorDocument.number_document.$touch()"
          :placeholder="$t('number')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.number_document.$dirty && !$v.sailorDocument.number_document.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.sailorDocument.number_document.$dirty && !$v.sailorDocument.number_document.maxLength"
          :text="$t('tooLongSailorPassNum')"
        />
      </div>
      <div class="w-50">
        <b>{{ $t('captain') }}:</b>
        <span class="required-field-star">*</span>
        <b-input
          v-model="sailorDocument.captain"
          @blur="$v.sailorDocument.captain.$touch()"
          :placeholder="$t('captain')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.captain.$dirty && !$v.sailorDocument.captain.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.sailorDocument.captain.$dirty && !$v.sailorDocument.captain.maxLength"
          :text="$t('tooLongCaptName')"
        />
      </div>
      <div class="w-50">
        <b>{{ $t('dateIssue') }}:</b>
        <span class="required-field-star">*</span>
        <b-input-group>
          <b-form-input
            v-model="sailorDocument.date_start"
            @blur="$v.dateIssueObject.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="sailorDocument.date_start"
              @input="$v.dateIssueObject.$touch()"
              :locale="lang"
              :max="new Date()"
              min="1900-01-01"
              start-weekday="1"
              button-only
              right
            />
          </b-input-group-append>
        </b-input-group>
        <ValidationAlert
          v-if="$v.dateIssueObject.$dirty && !$v.dateIssueObject.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dateIssueObject.$dirty && (!$v.dateIssueObject.maxValue || !$v.dateIssueObject.minValue)"
          :text="$t('dateIssuedValid')"
        />
      </div>
      <div class="w-50">
        <b>{{ $t('dateTermValid') }}:</b>
        <span class="required-field-star">*</span>
        <b-input-group>
          <b-form-input
            v-model="sailorDocument.date_end"
            @blur="$v.dateTerminationObject.$touch()"
            type="date"
            required
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="sailorDocument.date_end"
              @input="$v.dateTerminationObject.$touch()"
              :locale="lang"
              :min="sailorDocument.date_start"
              max="2200-12-31"
              start-weekday="1"
              button-only
              required
              right
            />
          </b-input-group-append>
        </b-input-group>
        <ValidationAlert
          v-if="$v.dateTerminationObject.$dirty && !$v.dateTerminationObject.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dateTerminationObject.$dirty &&
          (!$v.dateTerminationObject.maxValue || !$v.dateTerminationObject.minValue)"
          :text="$t('dateTerminateValid')"
        />
      </div>
      <div
        v-if="!dateRenewal"
        class="w-100"
      >
        <b>{{ $t('dateRenewal') }}:</b>
        <b-input-group>
          <b-form-input
            v-model="sailorDocument.date_renewal"
            @blur="$v.dateRenewalObject.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="sailorDocument.date_renewal"
              @input="$v.dateRenewalObject.$touch()"
              :locale="lang"
              :min="sailorDocument.date_end"
              max="2200-12-31"
              start-weekday="1"
              button-only
              right
            />
          </b-input-group-append>
        </b-input-group>
        <ValidationAlert
          v-if="$v.dateRenewalObject.$dirty && (!$v.dateRenewalObject.maxValue || !$v.dateRenewalObject.minValue)"
          :text="$t('dateRenewalValid')"
        />
      </div>

      <div>
        <FileDropZone ref="mediaContent" class="w-100 p-0" />
      </div>
      <div>
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
            @click="checkEditedDocument()"
            variant="success"
          >
            {{ $t('save') }}
          </b-button>
        </b-overlay>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorPassportEdit.js"/>
