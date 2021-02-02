<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-50">
        <label>
          {{ $t('city') }}
          <span class="requared-field-star">*</span>
        </label>
        <multiselect
          v-model="city"
          @input="mappingCertApplicationInstitution"
          :searchable="true"
          :placeholder="$t('city')"
          :options="institutionsCity"
        />
        <ValidationAlert
          v-if="$v.city.$dirty && !$v.city.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-50">
        <label>
          {{ $t('meetingDate') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-input-group>
          <b-form-input
            v-model="dateMeeting"
            @blur="$v.dateMeetingObject.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="dateMeeting"
              @hidden="$v.dateMeetingObject.$touch()"
              :locale="lang"
              min="1900-01-01"
              max="2200-01-01"
              start-weekday="1"
              button-only
              right
            />
          </b-input-group-append>
        </b-input-group>
        <ValidationAlert
          v-if="$v.dateMeetingObject.$dirty && !$v.dateMeetingObject.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dateMeetingObject.$dirty && (!$v.dateMeetingObject.minValue || !$v.dateMeetingObject.minValue)"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-100 mt-1">
        <label>
          {{ $t('nameInstitution') }}
          <span class="requared-field-star">*</span>
        </label>
        <multiselect
          v-model="eti"
          :options="filteredInstitutionsList[0] ? filteredInstitutionsList[0] : []"
          :custom-label="customLabelView"
          :preselect-first="true"
          :searchable="true"
          :showLabels="false"
          :placeholder="$t('nameInstitution')"
        >
          <template slot="noOptions">
            <span v-if="!city">{{ $t('selectCourseAndCity') }}</span>
            <span v-else>{{ $t('notFoundEti') }}</span>
          </template>

          <template slot="option" slot-scope="institution">
            <!--<div :class="{
              'green-option': institution.option.status === 'green-option',
              'grey-option': institution.option.status === 'grey-option',
              'red-option': institution.option.status === 'red-option'
            }">
              {{ institution.option.institutionName }}
              <span v-if="institution.option.status === 'green-option'">{{ $t('fastProcessing') }}</span>
              <span v-else-if="institution.option.status === 'grey-option'">{{ $t('normalProcessing') }}</span>
              <span v-else>{{ $t('slowProcessing') }}</span>
            </div>-->
            {{ institution.option.institutionName }}
          </template>
        </multiselect>
        <ValidationAlert
          v-if="$v.eti.$dirty && !$v.eti.required"
          :text="$t('emptyField')"
        />
      </div>

      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100 text-center mt-2"
        spinner-small
      >
        <b-button
          @click="checkEditedRecord"
          type="submit"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorCertificationStatementEdit.js"/>
