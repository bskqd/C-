<template>
  <b-card header-tag="header">
    <div>
      <div
        v-if="checkAccess('sailorSQCStatement', 'showPayment', sailorDocument)"
        class="text-left flex-row-sb"
      >
        <div class="col-12">
          <label class="text-bold-600">
            {{ $t('payment') }}:
          </label>
          <multiselect
            v-model="payment"
            :options="paymentStatus"
            :placeholder="$t('payment')"
            :searchable="true"
            :allow-empty="false"
            :label="labelName"
            track-by="id"
          />
        </div>
      </div>
      <div class="text-left flex-row-sb">
        <div
          v-if="checkAccess('sailorSQCStatement', 'showStatuses', sailorDocument)"
          class="col-12"
        >
          <label class="text-bold-600">
            {{ $t('status') }}:
          </label>
          <multiselect
            v-model="status"
            :options="mappingStatuses"
            :placeholder="$t('solution')"
            :allow-empty="false"
            :searchable="true"
            :label="labelName"
            track-by="id"
          />
        </div>
        <div
          v-else-if="checkAccess('sailorSQCStatement', 'showStudentStatuses', sailorDocument)"
          class="col-12"
        >
          <label class="text-bold-600">
            {{ $t('solution') }}:
          </label>
          <multiselect
            v-model="status"
            :options="mappingStudentStatuses"
            :placeholder="$t('solution')"
            :allow-empty="false"
            :searchable="true"
            :label="labelName"
            track-by="id"
          />
        </div>
      </div>
      <div
        v-if="checkAccess('sailorSQCStatement', 'requiredFile', sailorDocument)"
        class="col-12 text-left mt-2"
      >
        <FileDropZone ref="mediaContent" />
        <ValidationAlert
          v-if="$v.mediaFilesArray.$dirty && !$v.mediaFilesArray.required"
          :text="$t('emptyField')"
        />
      </div>
      <div class="col-12 d-flex justify-content-around mt-1">
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
            v-if="checkAccess('sailorSQCStatement', 'showSuccessButton', sailorDocument)"
            @click="checkForm(null)"
            variant="success"
          >
            {{ checkAccess('sailorSQCStatement', 'showSaveLabel', sailorDocument) ? $t('save') : $t('setVerify') }}
          </b-button>
        </b-overlay>

        <b-overlay
          :show="buttonLoaderReject"
          spinner-variant="primary"
          opacity="0.65"
          blur="2px"
          variant="white"
          class="w-100"
          spinner-small
        >
          <b-button
            v-if="checkAccess('sailorSQCStatement', 'showRejectButton', sailorDocument)"
            @click="checkForm(23)"
            variant="danger"
          >
            {{ $t('setReject') }}
          </b-button>
        </b-overlay>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorSQCStatementEditStatus.js" />
