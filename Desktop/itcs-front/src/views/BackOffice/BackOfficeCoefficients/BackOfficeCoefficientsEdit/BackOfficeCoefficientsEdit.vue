<template>
  <b-card header-tag="header">
    <b-form @submit.prevent="validateForm">
      <div class="seafarerInfoList">
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

        <div class="w-33">
          <label>
            {{ $t('etiPercent') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.percent_of_eti"
            @input="countProfitPercent"
            @blur="$v.sailorDocument.percent_of_eti.$touch()"
            :placeholder="$t('etiPercent')"
            type="number"
            step="0.01"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.percent_of_eti.$dirty && (!$v.sailorDocument.percent_of_eti.required || !$v.sailorDocument.percent_of_eti.minValue)"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.sailorDocument.percent_of_eti.$dirty && !$v.sailorDocument.percent_of_eti.maxValue"
            :text="$t('invalidDataFormat')"
          />
        </div>

        <div class="w-33">
          <label>
            {{ $t('profitPercent') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.percent_of_profit"
            @input="countPercentETI"
            @blur="$v.sailorDocument.percent_of_profit.$touch()"
            :placeholder="$t('profitPercent')"
            type="number"
            step="0.01"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.percent_of_profit.$dirty &&
              (!$v.sailorDocument.percent_of_profit.required || !$v.sailorDocument.percent_of_profit.minValue)"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.sailorDocument.percent_of_profit.$dirty && !$v.sailorDocument.percent_of_profit.maxValue"
            :text="$t('invalidDataFormat')"
          />
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
            >
              {{ $t('save') }}
            </b-button>
          </b-overlay>
        </div>
      </div>
    </b-form>
  </b-card>
</template>

<script src="./BackOfficeCoefficientsEdit.js" />
