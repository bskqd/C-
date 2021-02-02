<template>
  <b-form @submit.prevent="checkEditedRecord">
    <b-card header-tag="header">
      <div class="seafarerInfoList">
        <div>
          <b>{{ $t('number') }}:</b>
          <span class="required-field-star">*</span>
          <b-input
            v-model="number"
            @blur="$v.number.$touch()"
            :placeholder="$t('number')"
            type="number"
          />
          <ValidationAlert
            v-if="$v.number.$dirty && !$v.number.required"
            :text="$t('emptyField')"
          />
        </div>

        <div>
          <b>{{ $t('medicalInstitution') }}:</b>
          <span class="required-field-star">*</span>
          <multiselect
            v-model="medicalInstitution"
            @input="doctor = null"
            :options="mappingMedicalInstitutions"
            :placeholder="$t('medicalInstitution')"
            :allow-empty="false"
            :searchable="true"
            label="value"
            track-by="id"
          />
        </div>

        <div>
          <b>{{ $t('doctor') }}:</b>
          <span class="required-field-star">*</span>
          <multiselect
            v-model="doctor"
            @blur="$v.doctor.$touch()"
            :options="mappingDoctors"
            :placeholder="$t('doctor')"
            :searchable="true"
            label="FIO"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.doctor.$dirty && !$v.doctor.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="w-50">
          <b>{{ $t('dateIssue') }}:</b>
          <span class="required-field-star">*</span>
          <b-input-group>
            <b-form-input
              v-model="sailorDocument.date_start"
              @blur="$v.dateIssuedObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="sailorDocument.date_start"
                @hidden="$v.dateIssuedObject.$touch()"
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
            v-if="$v.dateIssuedObject.$dirty && !$v.dateIssuedObject.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dateIssuedObject.$dirty && (!$v.dateIssuedObject.minValue || !$v.dateIssuedObject.maxValue)"
            :text="$t('dateIssuedValid')"
          />
        </div>
        <div class="w-50">
          <b>{{ $t('dateEnd') }}:</b>
          <span class="required-field-star">*</span>
          <b-input-group>
            <b-form-input
              v-model="sailorDocument.date_end"
              @blur="$v.dateTerminateObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="sailorDocument.date_end"
                @hidden="$v.dateTerminateObject.$touch()"
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
            v-if="$v.dateTerminateObject.$dirty && !$v.dateTerminateObject.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dateTerminateObject.$dirty && (!$v.dateTerminateObject.minValue || !$v.dateTerminateObject.maxValue)"
            :text="$t('invalidDataFormat')"
          />
        </div>
        <div>
          <b>{{ $t('position') }}:</b>
          <span class="required-field-star">*</span>
          <multiselect
            v-model="position"
            :options="mappingPositions"
            :placeholder="$t('position')"
            :searchable="true"
            :allow-empty="false"
            :label="labelName"
            track-by="id"
          />
        </div>
        <div>
          <b>{{ $t('limitation') }}:</b>
          <span class="required-field-star">*</span>
          <multiselect
            v-model="limitation"
            :options="mappingLimitations"
            :placeholder="$t('limitation')"
            :searchable="true"
            :allow-empty="false"
            :label="labelName"
            track-by="id"
          />
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
              type="submit"
              class="mt-1"
              variant="success"
            >
              {{ $t('save') }}
            </b-button>
          </b-overlay>
        </div>
      </div>
    </b-card>
  </b-form>
</template>

<script src="./SailorMedicalEdit.js"/>
