<template>
  <b-form @submit.prevent="validateForm">
    <div class="text-left">
      <div class="flex-row-sb form-group">
        <div class="col-4">
          <label>
            {{ $t('dateEffective') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateStart"
              @blur="$v.dateIssueObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateStart"
                @hidden="$v.dateIssueObject.$touch()"
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
            v-if="$v.dateIssueObject.$dirty && !$v.dateIssueObject.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dateIssueObject.$dirty && (!$v.dateIssueObject.maxValue || !$v.dateIssueObject.minValue)"
            :text="$t('useTodayDate')"
          />
        </div>

        <div class="col-4">
          <label>
            {{ $t('etiPercent') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input
            v-model="dataForm.ntzCoefficient"
            @input="countProfitPercent"
            @blur="$v.dataForm.ntzCoefficient.$touch()"
            :placeholder="$t('etiPercent')"
            type="number"
            step="0.01"
          />
          <ValidationAlert
            v-if="$v.dataForm.ntzCoefficient.$dirty && (!$v.dataForm.ntzCoefficient.required || !$v.dataForm.ntzCoefficient.minValue)"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.ntzCoefficient.$dirty && !$v.dataForm.ntzCoefficient.maxValue"
            :text="$t('invalidDataFormat')"
          />
        </div>

        <div class="col-4">
          <label>
            {{ $t('profitPercent') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input
            v-model="dataForm.profitPercent"
            @input="countPercentETI"
            @blur="$v.dataForm.profitPercent.$touch()"
            :placeholder="$t('profitPercent')"
            type="number"
            step="0.01"
          />
          <ValidationAlert
            v-if="$v.dataForm.profitPercent.$dirty && (!$v.dataForm.profitPercent.required || !$v.dataForm.profitPercent.minValue)"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.profitPercent.$dirty && !$v.dataForm.profitPercent.maxValue"
            :text="$t('invalidDataFormat')"
          />
        </div>
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
        class="mt-1"
        type="submit"
        variant="success"
      >
        {{ $t('save') }}
      </b-button>
    </b-overlay>
  </b-form>
</template>

<script src="./BackOfficeCoefficientsAdd.js" />
