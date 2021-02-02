<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="col-12">
        <b>{{ $t('status') }}:</b>
        <span class="required-field-star">*</span>
        <multiselect
          v-model="status"
          :allow-empty="false"
          :searchable="true"
          :placeholder="$t('status')"
          :options="mappingStatuses"
          :label="labelName"
          track-by="id"
        />
      </div>

      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="col-12 text-center"
        spinner-small
      >
        <b-button
          @click="saveNewStatus"
          class="mt-1"
          type="submit"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorStudentEditStatus.js"/>
