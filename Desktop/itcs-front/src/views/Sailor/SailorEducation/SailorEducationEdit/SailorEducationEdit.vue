<template>
  <b-card header-tag="header">
    <b-form @submit.prevent="checkEditedRecord">
      <div
        v-if="checkAccess('education', 'editRegistryNumber')"
        class="seafarerInfoList"
      >
        <div class="w-33">
          <b>{{ $t('registrationNumber') }}:</b>
          <span class="required-field-star">*</span>
          <b-input
            v-model="sailorDocument.registry_number"
            @blur="$v.sailorDocument.registry_number.$touch()"
            :placeholder="$t('registrationNumber')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.registry_number.$dirty && !$v.sailorDocument.registry_number.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="w-33">
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
            :text="$t('educNumLength')"
          />
        </div>
        <div class="w-33">
          <b>{{ $t('serial') }}:</b>
          <span class="required-field-star">*</span>
          <b-input
            v-model="sailorDocument.serial"
            @blur="$v.sailorDocument.serial.$touch()"
            :placeholder="$t('serial')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.serial.$dirty && !$v.sailorDocument.serial.required"
            :text="$t('emptyField')"
          />
        </div>

        <div
          v-if="viewDiploma"
          class="w-50"
        >
          <b>{{ $t('educationExtent') }}:</b>
          <span class="required-field-star">*</span>
          <multiselect
            v-model="sailorDocument.extent"
            :options="mappingExtent"
            :placeholder="$t('educationExtent')"
            :allow-empty="false"
            :searchable="true"
            :label="langFields"
            track-by="id"
          />
        </div>

        <div>
          <b>{{ $t('nameInstitution') }}:</b>
          <span class="required-field-star">*</span>
          <multiselect
            v-model="sailorDocument.name_nz"
            :options="mappingInstitution"
            :placeholder="$t('nameInstitution')"
            :allow-empty="false"
            :searchable="true"
            :label="langFields"
            track-by="id"
          />
        </div>

        <div>
          <b>{{ $t('qualification') }}:</b>
          <span class="required-field-star">*</span>
          <multiselect
            v-model="sailorDocument.qualification"
            :options="mappingQualification(sailorDocument.type_document)"
            :placeholder="$t('qualification')"
            :allow-empty="false"
            :searchable="true"
            :label="langFields"
            track-by="id"
          />
        </div>
        <div v-if="viewProfession">
          <b v-if="sailorDocument.type_document.id === 1">
            {{ $t('specialty') }}
            <span class="required-field-star">*</span>
          </b>
          <b v-if="sailorDocument.type_document.id === 2">
            {{ $t('profession') }}
            <span class="required-field-star">*</span>
          </b>

          <multiselect
            v-model="sailorDocument.speciality"
            :options="mappingProfession(sailorDocument.type_document)"
            :allow-empty="false"
            :searchable="true"
            :placeholder="$t('profession')"
            :label="langFields"
            track-by="id"
          />
        </div>
        <div v-if="viewDiploma && viewSpecialization">
          <b>{{ $t('specialization') }}:</b>
          <span class="required-field-star">*</span>
          <multiselect
            v-model="sailorDocument.specialization"
            :options="mappingSpecialization(sailorDocument.speciality, sailorDocument.specialization)"
            :searchable="true"
            :placeholder="$t('specialization')"
            :label="langFields"
            track-by="id"
          >
            <span slot="noOptions">
              {{ $t('noProvided') }}
            </span>
          </multiselect>
        </div>
        <div>
          <b>{{ $t('duplicate') }}: </b>
          <b-form-checkbox
            v-model="sailorDocument.is_duplicate"
            :value="true"
            :unchecked-value="false"
            class="pt-0 pl-5"
          />
        </div>

        <div>
          <b>{{ $t('notes') }}:</b>
          <b-input
            v-model="sailorDocument.special_notes"
            :placeholder="$t('notes')"
            type="text"
          />
        </div>

        <div class="w-33">
          <b>{{ $t('dateIssue') }}:</b>
          <span class="required-field-star">*</span>
          <b-input-group>
            <b-form-input
              v-model="sailorDocument.date_issue_document"
              @blur="$v.dateIssuedObject.$touch()"
              type="date"
              required
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="sailorDocument.date_issue_document"
                @input="$v.dateIssuedObject.$touch()"
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
            v-if="$v.dateIssuedObject.$dirty && !$v.dateIssuedObject.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dateIssuedObject.$dirty && (!$v.dateIssuedObject.maxValue || !$v.dateIssuedObject.minValue)"
            :text="$t('dateIssuedValid')"
          />
        </div>
        <div
          v-if="viewYearEnd"
          class="w-33"
        >
          <b>{{ $t('yearEndEducation') }}:</b>
          <span class="required-field-star">*</span>
          <b-form-input
            v-model="yearTermination"
            @blur="$v.yearTermination.$touch()"
            :placeholder="$t('yearEndEducation')"
            type="number"
            step="1"
            required
          />
          <ValidationAlert
            v-if="$v.yearTermination.$dirty && !$v.yearTermination.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.yearTermination.$dirty &&
              (!$v.yearTermination.minValue || !$v.yearTermination.maxValue)"
            :text="$t('dateEndInvalid')"
          />
        </div>
        <div
          v-if="viewDateEnd"
          class="w-33"
        >
          <b>{{ $t('dateEndEducation') }}:</b>
          <span class="required-field-star">*</span>
          <b-input-group>
            <b-form-input
              v-model="sailorDocument.date_end_educ"
              @blur="$v.dateEndObject.$touch()"
              type="date"
              required
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="sailorDocument.date_end_educ"
                @input="$v.dateEndObject.$touch()"
                :locale="lang"
                :max="sailorDocument.date_issue_document"
                min="1900-01-01"
                start-weekday="1"
                button-only
                required
                right
              />
            </b-input-group-append>
          </b-input-group>
          <ValidationAlert
            v-if="$v.dateEndObject.$dirty && !$v.dateEndObject.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dateEndObject.$dirty && (!$v.dateEndObject.maxValue || !$v.dateEndObject.minValue)"
            :text="$t('dateEndInvalid')"
          />
        </div>

      </div>
      <div class="seafarerInfoList">
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
              type="submit"
              variant="success"
              class="mt-1"
            >
              {{ $t('save') }}
            </b-button>
          </b-overlay>
        </div>
      </div>
    </b-form>
  </b-card>
</template>

<script src="./SailorEducationEdit.js"/>
