<template>
  <b-form @submit.prevent="validateForm">
    <div class="text-left">
      <div class="flex-row-sb form-group">
        <div class="col-4">
          <label>
            {{ $t('number') }}
          </label>
          <b-input
            v-model="dataForm.number"
            :placeholder="$t('number')"
            type="text"
          />
        </div>
        <div class="col-4">
          <label>
            {{ $t('serial') }}
          </label>
          <b-input
            v-model="dataForm.serial"
            :placeholder="$t('serial')"
            type="text"
          />
        </div>
        <div class="col-4">
          <label>
            {{ $t('group') }}
          </label>
          <b-input
            v-model="dataForm.group"
            :placeholder="$t('group')"
            type="text"
          />
        </div>
      </div>

      <div class="flex-row-sb form-group">
        <div class="col-12">
          <label>
            {{ $t('nameInstitution') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.institution"
            @close="$v.dataForm.institution.$touch()"
            :searchable="true"
            :placeholder="$t('nameInstitution')"
            :options="mappingInstitution"
            :label="labelName"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.institution.$dirty && !$v.dataForm.institution.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div class="flex-row-sb form-group">
        <div class="col-12">
          <label>
            {{ $t('way') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.faculty"
            @close="$v.dataForm.faculty.$touch()"
            :placeholder="$t('faculty')"
            :options="mappingFaculties"
            :label="labelName"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.faculty.$dirty && !$v.dataForm.faculty.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div class="flex-row-sb form-group">
        <div class="col-12">
          <label>
            {{ $t('educationForm') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.educationForm"
            @close="$v.dataForm.educationForm.$touch()"
            :searchable="true"
            :placeholder="$t('educationForm')"
            :options="mappingEducForm"
            :label="labelName"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.educationForm.$dirty && !$v.dataForm.educationForm.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div class="flex-row-sb form-group">
        <div class="col-6">
          <label>
            {{ $t('dataEnrollment') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateStart"
              @blur="$v.dateStartObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateStart"
                @hidden="$v.dateStartObject.$touch()"
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
            v-if="$v.dateStartObject.$dirty && !$v.dateStartObject.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-if="$v.dateStartObject.$dirty && (!$v.dateStartObject.maxValue || !$v.dateStartObject.minValue)"
            :text="$t('dateIssuedValid')"
          />
        </div>
        <div class="col-6">
          <label>
            {{ $t('dateEnd') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateEnd"
              @blur="$v.dateEndObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateEnd"
                @hidden="$v.dateEndObject.$touch()"
                :locale="lang"
                :min="dataForm.dateStart"
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
      </div>

      <div class="flex-row-sb form-group">
        <div class="col-12">
          <label>
            {{ $t('status') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.status"
            @close="$v.dataForm.status.$touch()"
            :searchable="true"
            :placeholder="$t('status')"
            :options="mappingStatuses"
            :label="labelName"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.status.$dirty && !$v.dataForm.status.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div class="col-12 form-group">
        <b-form-checkbox
          v-model="dataForm.educationWithSQC"
          :value="true"
          :unchecked-value="false"
          class="mt-1 mr-1"
        >
          {{ $t('educationWithSQC') }}
        </b-form-checkbox>
      </div>

      <div class="col-12 form-group">
        <b-form-checkbox
          v-model="dataForm.passedEducationExam"
          :value="true"
          :unchecked-value="false"
          class="mt-1 mr-1"
        >
          {{ $t('passedEducationExam') }}
        </b-form-checkbox>
      </div>

      <div class="col-12 form-group text-left">
        <FileDropZone ref="mediaContent" />
      </div>

      <b-overlay
        :show="dataForm.buttonLoader"
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
</template>

<script src="./SailorStudentAdd.js"/>
