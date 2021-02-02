<template>
  <b-form @submit.prevent="validateForm">
    <div class="text-left">
      <div class="w-100 mt-3">
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
          v-else-if="$v.dataForm.number.$dirty && !$v.dataForm.number.numeric"
          :text="$t('onlyNumeric')"
        />
      </div>
      <div class="w-100 mt-3">
        <label>
          {{ $t('passportIssued') }}
          <span class="required-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.eti"
          @close="$v.dataForm.eti.$touch()"
          :options="mappingETI"
          :searchable="true"
          :placeholder="$t('passportIssued')"
          :label="labelName"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataForm.eti.$dirty && !$v.dataForm.eti.required"
          :text="$t('emptyField')"
        />
      </div>
      <div class="w-100 mt-3">
        <label>
          {{ $t('course') }}
          <span class="required-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.course"
          @close="$v.dataForm.course.$touch()"
          :options="mappingCourses"
          :searchable="true"
          :allow-empty="false"
          :placeholder="$t('course')"
          deselect-label=""
          :label="labelName"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataForm.course.$dirty && !$v.dataForm.course.required"
          :text="$t('emptyField')"
        />
      </div>
      <div class="flex-row-sb form-group mt-2">
        <div class="col-6">
          <label>
            {{ $t('dateIssue') }}
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
            v-if="$v.dateStartObject.$dirty &&
              (!$v.dateStartObject.maxValue || !$v.dateStartObject.minValue)"
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
            v-if="$v.dateEndObject.$dirty && !$v.dateEndObject.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-if="$v.dateEndObject.$dirty &&
              (!$v.dateEndObject.maxValue || !$v.dateEndObject.minValue)"
            :text="$t('dateTerminateValid')"
          />
        </div>
      </div>
      <div class="w-100">
        <label>
          {{ $t('status') }}
          <span class="required-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.status"
          @close="$v.dataForm.status.$touch()"
          :options="mappingStatuses"
          :searchable="true"
          :allow-empty="false"
          :placeholder="$t('status')"
          deselect-label=""
          :label="labelName"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataForm.status.$dirty && !$v.dataForm.status.required"
          :text="$t('emptyField')"
        />
      </div>
      <div
        v-if="checkAccess('backOffice')"
        class="w-100"
      >
        <b-form-checkbox
          v-model="dataForm.onlyForDPD"
          :value="true"
          :unchecked-value="false"
          class="mt-1 mr-1"
        >
          {{ $t('onlyForDPD') }}
        </b-form-checkbox>
      </div>
    </div>
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
      >
        {{ $t('save') }}
      </b-button>
    </b-overlay>
  </b-form>
</template>

<script src="./SailorCertificationAdd.js"/>
