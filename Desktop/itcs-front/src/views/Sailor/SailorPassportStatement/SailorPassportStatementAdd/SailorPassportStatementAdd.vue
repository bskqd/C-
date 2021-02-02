<template>
  <b-form @submit.prevent="checkFields">
    <div class="d-flex wrap text-left">
      <div class="w-100 pl-1 pr-1 mb-1 position-relative">
        <label>
          {{ $t('receiveDoc') }}
          <span class="requared-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.processingMethod"
          @close="$v.dataForm.processingMethod.$touch()"
          :options="processingOptionsList"
          :searchable="true"
          :placeholder="$t('receiveDoc')"
          :label="labelName"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataForm.processingMethod.$dirty && !$v.dataForm.processingMethod.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-100 pl-1 pr-1 mb-1 position-relative">
        <label>
          {{ $t('port') }}
          <span class="requared-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.port"
          @close="$v.dataForm.port.$touch()"
          :options="ports"
          :searchable="true"
          :placeholder="$t('port')"
          :label="labelName"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataForm.port.$dirty && !$v.dataForm.port.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-100 p-0 position-relative">
        <FileDropZone ref="mediaContent" />
      </div>

      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100 text-center mt-1"
        spinner-small
      >
        <b-button
          type="submit"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-form>
</template>

<script src="./SailorPassportStatementAdd.js" />

<style scoped>

</style>
