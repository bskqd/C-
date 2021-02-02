<template>
  <b-card header-tag="header">
    <b-form @submit.prevent="validateForm">
      <div class="seafarerInfoList">
        <div class="w-33">
          <label>
            {{ $t('numberProtocol') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.full_number_protocol"
            @blur="$v.sailorDocument.full_number_protocol.$touch()"
            :placeholder="$t('numberProtocol')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.full_number_protocol.$dirty && !$v.sailorDocument.full_number_protocol.required"
            :text="$t('emptyField')"
          />
        </div>

<!--        <div class="w-50">-->
<!--          <label>-->
<!--            {{ $t('course') }}-->
<!--            <span class="requared-field-star">*</span>-->
<!--          </label>-->
<!--          <multiselect-->
<!--            v-model="sailorDocument.course"-->
<!--            :searchable="true"-->
<!--            :placeholder="$t('course')"-->
<!--            :options="mappingCourses"-->
<!--            :label="labelName"-->
<!--            track-by="id"-->
<!--          />-->
<!--          <ValidationAlert-->
<!--            v-if="$v.sailorDocument.course.$dirty && !$v.sailorDocument.course.required"-->
<!--            :text="$t('emptyField')"-->
<!--          />-->
<!--        </div>-->

        <div class="w-33">
          <label>
            {{ $t('dateEffective') }}
            <span class="requared-field-star">*</span>
          </label>
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
                min="1900-00-01"
                max="2200-01-01"
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
            v-else-if="$v.dateStartObject.$dirty && (!$v.dateStartObject.maxValue || !$v.dateStartObject.minValue)"
            :text="$t('invalidDataFormat')"
          />
        </div>

        <div class="w-33">
          <label>
            {{ $t('dateTermination') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input-group>
            <b-form-input
              v-model="sailorDocument.date_end"
              @blur="$v.dateEndObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="sailorDocument.date_end"
                @hidden="$v.dateEndObject.$touch()"
                :locale="lang"
                min="1900-00-01"
                max="2200-01-01"
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
            v-else-if="$v.dateEndObject.$dirty && (!$v.dateEndObject.maxValue || !$v.dateEndObject.minValue)"
            :text="$t('invalidDataFormat')"
          />
        </div>

        <div class="w-100 pl-1 pr-1">
          <b-form-checkbox
            v-model="sailorDocument.is_disable"
            :value="true"
            :unchecked-value="false"
            class="mt-1 mr-1"
          >
            {{ $t('isDisable') }}
          </b-form-checkbox>
        </div>

        <b-overlay
          :show="buttonLoader"
          spinner-variant="primary"
          opacity="0.65"
          blur="2px"
          variant="white"
          class="w-100 text-center"
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

<script src="./BackOfficeCoursesEdit.js" />
