<template>
  <b-card>
    <b-form @submit.prevent="checkSavingNewCity">
      <div class="pageList p-0">
        <div class="w-33">
          <b>{{ $t('selectCountry')}}</b>
          <multiselect
            v-model="dataForm.country"
            @close="$v.dataForm.country.$touch()"
            :searchable="true"
            :options="mappingCountry"
            :placeholder="$t('country')"
            :label="labelValue"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.country.$dirty && !$v.dataForm.country.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="w-33">
          <b>{{ $t('selectRegion')}}</b>
          <multiselect
            v-model="dataForm.region"
            @close="$v.dataForm.region.$touch()"
            :searchable="true"
            :options="mappingRegion(dataForm.country)"
            :placeholder="$t('region')"
            :label="labelValue"
            track-by="id"
          >
            <span slot="noOptions">{{ $t('selectCountry') }}</span>
          </multiselect>
          <ValidationAlert
            v-if="$v.dataForm.region.$dirty && !$v.dataForm.region.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="w-33">
          <b>{{ $t('selectCityType')}}</b>
          <multiselect
            v-model="dataForm.typeCity"
            @close="$v.dataForm.typeCity.$touch()"
            :searchable="true"
            :options="cityType"
            :placeholder="$t('selectCityType')"
            :label="labelName"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.typeCity.$dirty && !$v.dataForm.typeCity.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="w-50">
          <b>{{ $t('enterCityUkr')}}</b>
          <b-input
            v-model.trim="dataForm.cityUkr"
            @blur="$v.dataForm.cityUkr.$touch()"
            :placeholder="$t('enterCityUkr')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataForm.cityUkr.$dirty && !$v.dataForm.cityUkr.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.cityUkr.$dirty && !$v.dataForm.cityUkr.alphaUA"
            :text="$t('noAlphaUA')"
          />
        </div>
        <div class="w-50">
          <b>{{ $t('enterCityEng')}}</b>
          <b-input
            v-model.trim="dataForm.cityEng"
            @blur="$v.dataForm.cityEng.$touch()"
            :placeholder="$t('enterCityEng')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataForm.cityEng.$dirty && !$v.dataForm.cityEng.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.cityEng.$dirty && !$v.dataForm.cityEng.alphaEN"
            :text="$t('noAlpha')"
          />
        </div>
        <div class="flex-row-sb form-group text-left">
          <div class="col-12 text-center">
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
                class="mt-2"
              >
                {{ $t('save') }}
              </b-button>
            </b-overlay>
          </div>
        </div>
      </div>
    </b-form>
  </b-card>
</template>

<script src="./DirectoryAddress.js"></script>
