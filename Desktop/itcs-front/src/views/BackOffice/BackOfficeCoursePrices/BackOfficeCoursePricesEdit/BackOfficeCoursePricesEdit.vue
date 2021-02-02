<template>
  <b-card header-tag="header">
    <b-form @submit.prevent="checkCoursePrice">
      <div class="seafarerInfoList">
        <div class="w-33">
          <label>
            {{ $t('dateEffective') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input-group>
            <b-form-input
              v-model="dateStart"
              @blur="$v.dateStartObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dateStart"
                @hidden="$v.dateStartObject.$touch()"
                :locale="lang"
                :min="dateTomorrow"
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
            :text="$t('useTodayDate')"
          />
        </div>

<!--        <div class="w-50">
          <label>
            {{ $t('course') }}
            <span class="requared-field-star">*</span>
          </label>
          <multiselect
            v-model="course"
            :searchable="true"
            :placeholder="$t('course')"
            :options="mappingCourses"
            :label="labelName"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.course.$dirty && !$v.course.required"
            :text="$t('emptyField')"
          />
        </div>-->

        <div class="w-33">
          <label>
            {{ $t('price') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input
            v-model="price"
            @blur="$v.price.$touch()"
            :placeholder="$t('price')"
            type="number"
            step="0.01"
          />
          <ValidationAlert
            v-if="$v.price.$dirty && !$v.price.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.price.$dirty && !$v.price.minValue"
            :text="$t('invalidDataFormat')"
          />
        </div>

        <div class="w-33">
          <label>
            {{ $t('priceForm') }}
            <span class="requared-field-star">*</span>
          </label>
          <multiselect
            v-model="formType"
            :searchable="true"
            :placeholder="$t('priceForm')"
            :options="formTypeList"
            :label="lang"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.formType.$dirty && !$v.formType.required"
            :text="$t('emptyField')"
          />
        </div>

        <b-overlay
          :show="buttonLoader"
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
  </b-card>
</template>

<script src="./BackOfficeCoursePricesEdit.js" />
