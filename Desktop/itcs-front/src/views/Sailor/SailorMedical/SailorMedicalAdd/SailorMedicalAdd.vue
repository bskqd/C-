<template>
  <b-form @submit.prevent="checkInfo">
    <div class="text-left">
      <div class="flex-row-sb form-group">
        <div class="col-12">
          <label>
            {{ $t('number') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="dataForm.number"
            @blur="$v.dataForm.number.$touch()"
            :placeholder="$t('number')"
            type="number"
          />
          <ValidationAlert
            v-if="$v.dataForm.number.$dirty && !$v.dataForm.number.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div class="flex-row-sb form-group mt-2">
        <div class="col-12">
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
      </div>

      <div class="flex-row-sb form-group mt-2">
        <div class="col-12">
          <label>
            {{ $t('limitation') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.limitation"
            :options="mappingLimitations"
            :placeholder="$t('limitation')"
            :searchable="true"
            :allow-empty="false"
            :label="labelName"
            track-by="id"
          />
        </div>
      </div>

      <div class="flex-row-sb form-group mt-2">
        <div class="col-12">
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
      </div>

      <div class="flex-row-sb form-group mt-2">
        <div class="col-12">
          <label>
            {{ $t('doctor') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.doctor"
            @close="$v.dataForm.doctor.$touch()"
            :options="mappingDoctors(dataForm.medInstitution)"
            :placeholder="$t('doctor')"
            :searchable="true"
            label="FIO"
            track-by="id"
          >
            <span slot="noOptions">
              {{ $t('selectMedicalInstitution') }}
            </span>
          </multiselect>
          <ValidationAlert
            v-if="$v.dataForm.doctor.$dirty && !$v.dataForm.doctor.required"
            :text="$t('emptyField')"
          />
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
              v-model="dataForm.dateIssue"
              @blur="$v.dateIssuedObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateIssue"
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
        <div class="col-6">
          <label>
            {{ $t('dateTermination') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateEnd"
              @blur="$v.dateTerminateObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateEnd"
                @hidden="$v.dateTerminateObject.$touch()"
                :locale="lang"
                :min="dataForm.dateIssue"
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
      </div>

      <div class="col-12 form-group text-left mt-2">
        <FileDropZone ref="mediaContent" />
      </div>
    </div>
    <div class="form-group text-center mb-0">
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
    </div>
  </b-form>
</template>

<script src="./SailorMedicalAdd.js"/>
