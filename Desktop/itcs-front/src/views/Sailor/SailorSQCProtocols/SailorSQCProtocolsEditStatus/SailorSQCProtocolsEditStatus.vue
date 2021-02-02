<template>
  <b-card header-tag="header">
    <div class="text-left">
      <div class="form-group col-12">
        <label class="text-bold-600">
          {{ $t('status') }}:
          <span class="requaredFieldStar">*</span>
        </label>
        <multiselect
          v-model="status"
          :options="mappingStatuses"
          :searchable="true"
          :placeholder="$t('status')"
          :allow-empty="false"
          :label="labelName"
          track-by="id"
        />
      </div>
      <div class="form-group col-12">
        <label class="text-bold-600">
          {{ $t('solution') }}:
          <span class="requaredFieldStar">*</span>
        </label>
        <multiselect
          v-model="decision"
          :options="solutions"
          :searchable="true"
          :placeholder="$t('solution')"
          :allow-empty="false"
          :label="labelName"
          track-by="id"
        />
      </div>
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
          @click="saveStatus()"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorSQCProtocolsEditStatus.js" />

<style scoped>

</style>
