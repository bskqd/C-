<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-33">
        <b>{{ $t('number') }}:</b>
        <span class="requared-field-star">*</span>
        <b-form-input
          v-model="number"
          @blur="$v.number.$touch()"
          :placeholder="$t('number')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.number.$dirty && !$v.number.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-33">
        <b>{{ $t('dateIssue') }}:</b>
        <span class="requared-field-star">*</span>
        <b-input-group>
          <b-form-input
            v-model="dateIssued"
            @blur="$v.dateIssuedObject.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="dateIssued"
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
          :text="$t('notLateThenToday')"
        />
      </div>

      <div class="w-33">
        <b>{{ $t('dateTermValid') }}:</b>
        <span class="requared-field-star">*</span>
        <b-input-group>
          <b-form-input
            v-model="dateTerminated"
            @blur="$v.dateTerminatedObject.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="dateTerminated"
              @hidden="$v.dateTerminatedObject.$touch()"
              :locale="lang"
              :min="dateIssued"
              max="2200-12-31"
              start-weekday="1"
              button-only
              right
            />
          </b-input-group-append>
        </b-input-group>
        <ValidationAlert
          v-if="$v.dateTerminatedObject.$dirty && !$v.dateTerminatedObject.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dateTerminatedObject.$dirty && (!$v.dateTerminatedObject.minValue || !$v.dateTerminatedObject.maxValue)"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div
        v-if="checkAccess('backOffice')"
        class="w-100"
      >
        <b-form-checkbox
          v-model="onlyForDPD"
          :value="true"
          :unchecked-value="false"
          class="mt-1 mr-1"
        >
          {{ $t('onlyForDPD') }}
        </b-form-checkbox>
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
          @click="checkFields"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorCertificationEdit.js" />
