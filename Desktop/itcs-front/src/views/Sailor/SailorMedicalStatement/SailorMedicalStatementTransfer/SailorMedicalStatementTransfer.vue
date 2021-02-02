<template>
  <b-card header-tag="header">
    <div class="d-flex wrap text-left">
      <div class="w-50">
        <label>
          {{ $t('number') }}
          <span class="required-field-star">*</span>
        </label>
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

      <div class="w-50">
        <label>
          {{ $t('limitation') }}
          <span class="required-field-star">*</span>
        </label>
        <multiselect
          v-model="limitation"
          @close="$v.limitation.$touch()"
          :options="mappingLimitations"
          :placeholder="$t('limitation')"
          :searchable="true"
          :label="langFields"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.limitation.$dirty && !$v.limitation.required"
          :text="$t('emptyField')"
        />
      </div>

      <div
        v-if="checkAccess('medicalStatement', 'enterDoctor')"
        class="w-50 mt-1"
      >
        <label>
          {{ $t('doctor') }}
          <span class="required-field-star">*</span>
        </label>
        <multiselect
          v-model="doctor"
          @close="$v.doctor.$touch()"
          :options="mappingDoctors()"
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

      <div class="w-50 mt-1">
        <label>{{ $t('dateTermination') }}</label>
        <span class="requared-field-star">*</span>
        <b-input-group>
          <b-form-input
            v-model="dateEnd"
            @blur="$v.dateEndObject.$touch"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="dateEnd"
              @hidden="$v.dateEndObject.$touch()"
              :locale="lang"
              min="1900-01-01"
              max="2200-01-01"
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
          :text="$t('invalidDataFormat')"
        />
      </div>

      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100 text-center mt-3"
        spinner-small
      >
        <b-button
          @click="checkInfo"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorMedicalStatementTransfer.js" />
