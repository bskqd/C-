<template>
  <b-form @submit.prevent="checkFields">
    <div class="d-flex wrap text-left">
      <div class="w-100 pl-1 pr-1 mb-1 position-relative">
        <label>
          {{ $t('position') }}
          <span class="required-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.position"
          @close="$v.dataForm.position.$touch()"
          :options="mappingPositions"
          :searchable="true"
          :placeholder="$t('position')"
          :label="labelName"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataForm.position.$dirty && !$v.dataForm.position.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-100 pl-1 pr-1 mb-1 position-relative">
        <label>
          {{ $t('medicalInstitution') }}
          <span class="required-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.medInstitution"
          @close="$v.dataForm.medInstitution.$touch()"
          :options="mappingMedicalInstitutions"
          :placeholder="$t('medicalInstitution')"
          :searchable="true"
          label="value"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataForm.medInstitution.$dirty && !$v.dataForm.medInstitution.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-100 pl-1 pr-1 mb-1 position-relative">
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

<script src="./SailorMedicalStatementAdd.js" />
