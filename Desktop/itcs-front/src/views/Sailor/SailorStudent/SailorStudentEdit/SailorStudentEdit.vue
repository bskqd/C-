<template>
  <b-card header-tag="header">
    <b-form @submit.prevent="validateForm">
      <div class="seafarerInfoList">
        <div class="col-4">
          <b>{{ $t('number') }}:</b>
          <b-input
            v-model="sailorDocument.number"
            :placeholder="$t('number')"
            type="text"
          />
        </div>
        <div class="col-4">
          <b>{{ $t('serial') }}:</b>
          <b-input
            v-model="sailorDocument.serial"
            :placeholder="$t('number')"
            type="text"
          />
        </div>
        <div class="col-4">
          <b>{{ $t('group') }}:</b>
          <b-input
            v-model="sailorDocument.group"
            :placeholder="$t('group')"
            type="text"
          />
        </div>

        <div class="col-12">
          <b>{{ $t('nameInstitution') }}:</b>
          <span class="required-field-star">*</span>
          <multiselect
            v-model="sailorDocument.name_nz"
            @close="$v.sailorDocument.name_nz.$touch()"
            :searchable="true"
            :placeholder="$t('nameInstitution')"
            :options="mappingInstitution"
            :label="langFields"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.name_nz.$dirty && !$v.sailorDocument.name_nz.required"
            :text="$t('emptyField')"
          />
        </div>

        <div class="col-12">
          <b>{{ $t('way') }}:</b>
          <span class="required-field-star">*</span>
          <multiselect
            v-model="sailorDocument.faculty"
            @close="$v.sailorDocument.faculty.$touch()"
            :placeholder="$t('faculty')"
            :options="mappingFaculties"
            :label="langFields"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.faculty.$dirty && !$v.sailorDocument.faculty.required"
            :text="$t('emptyField')"
          />
        </div>

        <div class="col-12">
          <b>{{ $t('educationForm') }}:</b>
          <span class="required-field-star">*</span>
          <multiselect
            v-model="sailorDocument.education_form"
            @close="$v.sailorDocument.education_form.$touch()"
            :searchable="true"
            :placeholder="$t('educationForm')"
            :options="mappingEducForm"
            :label="langFields"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.education_form.$dirty && !$v.sailorDocument.education_form.required"
            :text="$t('emptyField')"
          />
        </div>

        <div class="col-6">
          <b>{{ $t('dataEnrollment') }}:</b>
          <span class="required-field-star">*</span>
          <b-input-group>
            <b-form-input
              v-model="sailorDocument.date_start"
              @blur="$v.dateStartObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="sailorDocument.date_start"
                @hidden="$v.dateStartObject.$touch()"
                :locale="lang"
                :max="new Date()"
                min="1900-01-01"
                start-weekday="1"
                button-only
                required
                right
              />
            </b-input-group-append>
          </b-input-group>
          <ValidationAlert
            v-if="$v.dateStartObject.$dirty && !$v.dateStartObject.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-if="$v.dateStartObject.$dirty && (!$v.dateStartObject.maxValue || !$v.dateStartObject.minValue)"
            :text="$t('dateIssuedValid')"
          />
        </div>
        <div class="col-6">
          <b>{{ $t('dateEnd') }}:</b>
          <b-input-group>
            <b-form-input
              v-model="sailorDocument.date_end"
              @blur="$v.dateEndObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="sailorDocument.date_end"
                @hidden="$v.dateStartObject.$touch()"
                :locale="lang"
                :min="sailorDocument.date_start"
                max="2200-12-31"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
          <ValidationAlert
            v-if="$v.dateEndObject.$dirty && (!$v.dateEndObject.maxValue || !$v.dateEndObject.minValue)"
            :text="$t('dateTerminateValid')"
          />
        </div>

        <div class="col-12 form-group">
          <b-form-checkbox
            v-model="sailorDocument.educ_with_dkk"
            :value="true"
            :unchecked-value="false"
            class="mr-1"
          >
            {{ $t('educationWithSQC') }}
          </b-form-checkbox>
        </div>

        <div class="col-12 form-group">
          <b-form-checkbox
            v-model="sailorDocument.passed_educ_exam"
            :value="true"
            :unchecked-value="false"
            class="mr-1"
          >
            {{ $t('passedEducationExam') }}
          </b-form-checkbox>
        </div>

        <div>
          <FileDropZone ref="mediaContent" class="w-100 p-0" />
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
            class="mt-1"
            type="submit"
            variant="success"
          >
            {{ $t('save') }}
          </b-button>
        </b-overlay>
      </div>
    </b-form>
  </b-card>
</template>

<script src="./SailorStudentEdit.js"/>
