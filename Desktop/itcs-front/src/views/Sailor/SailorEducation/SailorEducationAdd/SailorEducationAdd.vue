<template>
  <b-form @submit.prevent="checkNewDoc">
    <div class="text-left">
      <div class="flex-row-sb form-group">
        <div class="col-5">
          <label>
            {{ $t('typeDoc') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.type"
            @input="checkTypeDoc"
            @close="$v.dataForm.type.$touch()"
            :searchable="true"
            :placeholder="$t('typeDoc')"
            :options="mappingTypeDoc"
            :label="langFields"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.type.$dirty && !$v.dataForm.type.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="col-2">
          <label>
            {{ $t('registrationNumber') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="dataForm.registrationNumber"
            @blur="$v.dataForm.registrationNumber.$touch()"
            :placeholder="$t('registrationNumber')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataForm.registrationNumber.$dirty && !$v.dataForm.registrationNumber.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="col-1">
          <label>
            {{ $t('serial') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="dataForm.serial"
            @blur="$v.dataForm.serial.$touch()"
            :placeholder="$t('serial')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataForm.serial.$dirty && !$v.dataForm.serial.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="col-4">
          <label>
            {{ $t('number') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="dataForm.number"
            @blur="$v.dataForm.number.$touch()"
            :placeholder="$t('number')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataForm.number.$dirty && !$v.dataForm.number.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.number.$dirty && !$v.dataForm.number.maxLength"
            :text="$t('educNumLength')"
          />
        </div>
      </div>

      <h5 class="text-bold-600 mt-2">
        {{ $t('infoAboutSpecialization') }}:
      </h5>

      <div
        v-if="viewDiploma"
        class="flex-row-sb form-group"
      >
        <div class="col-12">
          <label>
            {{ $t('educationExtent') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.educationExtent"
            @close="$v.dataForm.educationExtent.$touch()"
            :options="mappingExtent"
            :searchable="true"
            :label="langFields"
            :placeholder="$t('educationExtent')"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.educationExtent.$dirty && !$v.dataForm.educationExtent.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div class="flex-row-sb form-group mt-2">
        <div class="col-12">
          <label>
            {{ $t('nameInstitution') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.nameInstitution"
            @close="$v.dataForm.nameInstitution.$touch()"
            :options="mappingInstitution"
            :searchable="true"
            :placeholder="$t('nameInstitution')"
            :label="langFields"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.nameInstitution.$dirty && !$v.dataForm.nameInstitution.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div class="flex-row-sb form-group mt-2">
        <div class="col-12">
          <label>
            {{ $t('qualification') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.qualification"
            @close="$v.dataForm.qualification.$touch()"
            :options="mappingQualification(dataForm.type, dataForm.qualification)"
            :searchable="true"
            :placeholder="$t('qualification')"
            :label="langFields"
            track-by="id"
          >
            <span slot="noOptions">
              {{ $t('selectDocType') }}
            </span>
          </multiselect>
          <ValidationAlert
            v-if="$v.dataForm.qualification.$dirty && !$v.dataForm.qualification.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div
        v-if="viewProfession"
        class="flex-row-sb form-group mt-2"
      >
        <div class="col-12">
          <label v-if="dataForm.type && dataForm.type.id === 1">
            {{ $t('specialty') }}
            <span class="required-field-star">*</span>
          </label>
          <label v-if="dataForm.type && dataForm.type.id === 2">
            {{ $t('profession') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.speciality"
            @input="clearSpecialization"
            @close="$v.dataForm.speciality.$touch()"
            :options="mappingProfession(dataForm.type)"
            :searchable="true"
            :placeholder="$t('profession')"
            :label="langFields"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.speciality.$dirty && !$v.dataForm.speciality.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div
        v-if="viewDiploma && viewSpecialization"
        class="flex-row-sb form-group mt-2"
      >
        <div class="col-12">
          <label>
            {{ $t('specialization') }}
          </label>
          <multiselect
            v-model="dataForm.specialization"
            :options="mappingSpecialization(dataForm.speciality, dataForm.specialization)"
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
      </div>

      <div class="flex-row-sb form-group mt-2">
        <div class="col-6">
          <label>
            {{ $t('dateIssue') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateIssued"
              @blur="$v.dateIssuedObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateIssued"
                @input="$v.dateIssuedObject.$touch()"
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
            v-if="$v.dateIssuedObject.$dirty &&
              (!$v.dateIssuedObject.maxValue || !$v.dateIssuedObject.minValue)"
            :text="$t('dateIssuedValid')"
          />
        </div>
        <div
          v-if="viewYearEnd"
          class="col-6"
        >
          <label>
            {{ $t('yearEndEducation') }}
            <span class="required-field-star">*</span>
          </label>
          <b-form-input
            v-model="dataForm.yearTermination"
            @blur="$v.dataForm.yearTermination.$touch()"
            :placeholder="$t('dateEndEducation')"
            type="number"
            step="1"
          >
          </b-form-input>
          <ValidationAlert
            v-if="$v.dataForm.yearTermination.$dirty && !$v.dataForm.yearTermination.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.yearTermination.$dirty &&
              (!$v.dataForm.yearTermination.minValue || !$v.dataForm.yearTermination.maxValue)"
            :text="$t('dateEndInvalid')"
          />
        </div>
        <div
          v-if="viewDateEnd"
          class="col-6"
        >
          <label>
            {{ $t('dateEndEducation') }}
            <span class="required-field-star">*</span>
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
                @input="$v.dateEndObject.$touch()"
                :locale="lang"
                :max="dataForm.dateIssued"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
          <ValidationAlert
            v-if="$v.dateEndObject.$dirty && !$v.dateEndObject.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-if="$v.dateEndObject.$dirty &&
              (!$v.dateEndObject.maxValue || !$v.dateEndObject.minValue)"
            :text="$t('dateEndInvalid')"
          />
        </div>
      </div>
<!--      <div class="form-group">-->
<!--        <div-->
<!--          v-if="viewDateTermination"-->
<!--          class="col-6"-->
<!--        >-->
<!--          <label>-->
<!--            {{ $t('dateTermination') }}-->
<!--            <span class="required-field-star">*</span>-->
<!--          </label>-->
<!--          <b-input-group>-->
<!--            <b-form-input-->
<!--              v-model="dataForm.dateTermination"-->
<!--              @blur="$v.dateTerminationObject.$touch()"-->
<!--              type="date"-->
<!--            />-->
<!--            <b-input-group-append>-->
<!--              <b-form-datepicker-->
<!--                v-model="dataForm.dateTermination"-->
<!--                @input="$v.dateTerminationObject.$touch()"-->
<!--                :locale="lang"-->
<!--                max="2200-12-31"-->
<!--                :min="dataForm.dateIssued"-->
<!--                start-weekday="1"-->
<!--                button-only-->
<!--                right-->
<!--              />-->
<!--            </b-input-group-append>-->
<!--          </b-input-group>-->
<!--          <ValidationAlert-->
<!--            v-if="$v.dateTerminationObject.$dirty && !$v.dateTerminationObject.required"-->
<!--            :text="$t('emptyField')"-->
<!--          />-->
<!--          <ValidationAlert-->
<!--            v-if="$v.dateTerminationObject.$dirty &&-->
<!--              (!$v.dateTerminationObject.maxValue || !$v.dateTerminationObject.minValue)"-->
<!--            :text="$t('dateEndInvalid')"-->
<!--          />-->
<!--        </div>-->
<!--      </div>-->
      <div class="flex-row-sb form-group mt-2">
        <div class="col-12">
          <label>
            {{ $t('notes') }}
          </label>
          <b-input
            v-model="dataForm.notes"
            :placeholder="$t('notes')"
            type="text"
          />
        </div>
      </div>

      <div class="col-12 form-group">
        <b-form-checkbox
          v-model="dataForm.isDuplicate"
          :value="true"
          :unchecked-value="false"
          class="mt-1 mr-1"
        >
          {{ $t('duplicate') }}
        </b-form-checkbox>
      </div>

      <div class="col-12 form-group text-left mt-2">
        <FileDropZone ref="mediaContent" />
      </div>
    </div>
    <b-overlay
      :show="dataForm.buttonLoader"
      spinner-variant="primary"
      opacity="0.65"
      blur="2px"
      variant="white"
      class="w-100"
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
  </b-form>
</template>

<script src="./SailorEducationAdd.js"/>
