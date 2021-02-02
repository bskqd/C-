<template>
  <b-form @submit.prevent="checkFields">
    <div class="d-flex wrap text-left">
      <div class="w-100 pl-1 pr-1 mb-1 position-relative">
        <label>
          {{ $t('qualification') }}
          <span class="required-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.qualification"
          @close="$v.dataForm.qualification.$touch()"
          :options="mappingQualification"
          :searchable="true"
          :placeholder="$t('qualification')"
          :label="labelName"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataForm.qualification.$dirty && !$v.dataForm.qualification.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-100 pl-1 pr-1 mb-1 position-relative">
        <label>
          {{ $t('nameInstitution') }}
          <span class="required-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.institution"
          @close="$v.dataForm.institution.$touch()"
          :options="mappingInstitution"
          :searchable="true"
          :placeholder="$t('nameInstitution')"
          :label="labelName"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataForm.institution.$dirty && !$v.dataForm.institution.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-100 p-0 mb-1 position-relative">
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

<script src="./SailorEducationStatementAdd.js" />
