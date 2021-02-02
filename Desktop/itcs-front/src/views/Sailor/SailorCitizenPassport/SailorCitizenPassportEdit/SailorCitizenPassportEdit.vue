<template>
  <div class="text-left">
    <div class="w-100">
      <b>
        {{ $t('citizenship') }}
        <span class="required-field-star">*</span>
      </b>
      <multiselect
        v-model="dataInfo.country"
        @close="$v.dataInfo.country.$touch()"
        :options="mappingCountry"
        :searchable="true"
        :placeholder="$t('country')"
        :label="labelValue"
        track-by="id"
      />
      <ValidationAlert
        v-if="$v.dataInfo.country.$dirty && !$v.dataInfo.country.required"
        :text="$t('emptyField')"
      />
    </div>

    <div class="w-50">
      <b>
        {{ $t('serialAndNum') }}
        <span class="required-field-star">*</span>
      </b>
      <b-input
        v-model="dataInfo.serial"
        @blur="$v.dataInfo.serial.$touch()"
        :placeholder="$t('serialAndNum')"
        type="text"
      />
      <ValidationAlert
        v-if="$v.dataInfo.serial.$dirty && !$v.dataInfo.serial.required"
        :text="$t('emptyField')"
      />
      <ValidationAlert
        v-else-if="$v.dataInfo.serial.$dirty && !$v.dataInfo.serial.maxLength"
        :text="$t('seriesLength')"
      />
    </div>

    <div class="w-50">
      <b class="w-100 text-left">
        {{ $t('taxNumber') }}
        <span class="required-field-star">*</span>
      </b>
      <div class="w-100 d-flex">
        <div class="w-75 p-0">
          <b-input
            v-model="dataInfo.inn"
            @blur="$v.dataInfo.inn.$touch()"
            :placeholder="$t('taxNumber')"
            :disabled="absentITN"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataInfo.inn.$dirty && !$v.dataInfo.inn.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="w-25 d-flex align-items-center">
          <b-form-checkbox
            id="checkbox-1"
            v-model="absentITN"
            :value="true"
            :unchecked-value="false"
            class="pt-0 pl-3"
          >
            {{ $t('missing') }}
          </b-form-checkbox>
        </div>
      </div>
    </div>

    <div class="w-50">
      <b>
        {{ $t('dateIssue') }}
        <span class="required-field-star">*</span>
      </b>
      <b-input-group>
        <b-form-input
          v-model="dataInfo.date"
          @blur="$v.dateObject.$touch()"
          type="date"
        />
        <b-input-group-append>
          <b-form-datepicker
            v-model="dataInfo.date"
            @hidden="$v.dateObject.$touch()"
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
        v-if="$v.dateObject.$dirty && !$v.dateObject.required"
        :text="$t('emptyField')"
      />
      <ValidationAlert
        v-else-if="$v.dateObject.$dirty && (!$v.dateObject.minValue || !$v.dateObject.maxValue)"
        :text="$t('dateIssuedValid')"
      />
    </div>

    <div class="w-50">
      <b>
        {{ $t('passportIssued') }}
        <span class="required-field-star">*</span>
      </b>
      <b-input
        v-model="dataInfo.issued_by"
        @blur="$v.dataInfo.issued_by.$touch()"
        :placeholder="$t('passportIssued')"
        type="text"
      />
      <ValidationAlert
        v-if="$v.dataInfo.issued_by.$dirty && !$v.dataInfo.issued_by.required"
        :text="$t('emptyField')"
      />
      <ValidationAlert
        v-else-if="$v.dataInfo.issued_by.$dirty && !$v.dataInfo.issued_by.validPlaceIssued"
        :text="$t('invalidDataFormat')"
      />
    </div>

    <b class="w-100 mt-3 pl-3">{{ $t('registrationDoc') }}:</b>

    <div
      v-if="dataInfo && dataInfo.city_registration"
      class="w-100 d-flex"
    >
      <div class="w-30 p-0">
        <b>
          {{ $t('country') }}
          <span
            v-if="dataInfo.country && dataInfo.country.id === 2"
            class="required-field-star">*</span>
        </b>
        <multiselect
          v-model="dataInfo.city_registration.city.country"
          @close="$v.dataInfo.city_registration.city.country.$touch()"
          :value="dataInfo.country"
          :searchable="true"
          :options="mappingCountry"
          :placeholder="$t('country')"
          :label="labelValue"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataInfo.city_registration.city.country.$dirty &&
            !$v.dataInfo.city_registration.city.country.required"
          :text="$t('emptyField')"
        />
      </div>
      <div class="w-30">
        <b>
          {{ $t('region') }}
          <span v-if="dataInfo.country && dataInfo.country.id === 2"
            class="required-field-star">*</span>
        </b>
        <multiselect
          v-model="dataInfo.city_registration.city.region"
          @input="mappingCityList(dataInfo.city_registration.city.region, 'city_registration')"
          @close="$v.dataInfo.city_registration.city.region.$touch()"
          :searchable="true"
          :options="mappingRegion(dataInfo.city_registration.city.country)"
          :placeholder="$t('region')"
          :label="labelValue"
          track-by="id"
        >
          <span slot="noOptions">
            {{ $t('selectCountry') }}
          </span>
        </multiselect>
        <ValidationAlert
          v-if="$v.dataInfo.city_registration.city.region.$dirty &&
            !$v.dataInfo.city_registration.city.region.required"
          :text="$t('emptyField')"
        />
      </div>
      <div class="w-40 p-0">
        <b>
          {{ $t('city') }}
          <span v-if="dataInfo.country && dataInfo.country.id === 2"
            class="required-field-star">*</span>
        </b>
        <multiselect
          v-model="dataInfo.city_registration.city.city"
          @close="$v.dataInfo.city_registration.city.city.$touch()"
          :searchable="true"
          :options="registrationCitiesList"
          :placeholder="$t('city')"
          :label="labelValue"
          track-by="id"
        >
          <span slot="noOptions">
            {{ $t('selectRegion') }}
          </span>
        </multiselect>
        <ValidationAlert
          v-if="$v.dataInfo.city_registration.city.city.$dirty &&
            !$v.dataInfo.city_registration.city.city.required"
          :text="$t('emptyField')"
        />
      </div>
    </div>

    <div class="w-100 d-flex">
      <div class="w-20 p-0">
        <b>
          {{ $t('placeIndex') }}
          <span v-if="dataInfo.country && dataInfo.country.id === 2"
            class="required-field-star">*</span>
        </b>
        <b-input
          v-model="dataInfo.city_registration.index"
          @blur="$v.dataInfo.city_registration.index.$touch()"
          :placeholder="$t('placeIndex')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataInfo.city_registration.index.$dirty && !$v.dataInfo.city_registration.index.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataInfo.city_registration.index.$dirty &&
            (!$v.dataInfo.city_registration.index.maxLength || !$v.dataInfo.city_registration.index.minLength)"
          :text="$t('placeIndexCount')"
        />
      </div>
      <div class="w-50">
        <b>
          {{ $t('street') }}
          <span v-if="dataInfo.country && dataInfo.country.id === 2"
            class="required-field-star">*</span>
        </b>
        <b-input
          v-model="dataInfo.city_registration.street"
          @blur="$v.dataInfo.city_registration.street.$touch()"
          :placeholder="$t('street')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataInfo.city_registration.street.$dirty && !$v.dataInfo.city_registration.street.required"
          :text="$t('emptyField')"
        />
      </div>
      <div class="w-15 pl-0">
        <b>
          {{ $t('house') }}
          <span v-if="dataInfo.country && dataInfo.country.id === 2"
            class="required-field-star">*</span>
        </b>
        <b-input
          v-model="dataInfo.city_registration.house"
          @blur="$v.dataInfo.city_registration.house.$touch()"
          :placeholder="$t('house')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataInfo.city_registration.house.$dirty && !$v.dataInfo.city_registration.house.required"
          :text="$t('emptyField')"
        />
      </div>
      <div class="w-15 p-0">
        <b>{{ $t('flat') }}</b>
        <b-input
          v-model="dataInfo.city_registration.flat"
          :placeholder="$t('flat')"
          type="number"
        />
      </div>
    </div>

    <div class="w-100">
      <b-form-checkbox
        v-model="sameResidentPlace"
        name="bookPractical"
        class="mx-1"
        switch
      />
      <div v-if="sameResidentPlace">
        {{ $t('sameRegistration') }}
      </div>
      <div v-else>
        {{ $t('notSameRegistration') }}
      </div>
    </div>

    <div v-if="!sameResidentPlace" class="w-100 mt-3">
      <b class="mt-1">{{ $t('residentPlace') }}:</b>

      <div
        v-if="dataInfo && dataInfo.resident"
        class="w-100 p-0 d-flex"
      >
        <div class="w-30 p-0">
          <b>
            {{ $t('country') }}
            <span v-if="dataInfo.country && dataInfo.country.id === 2"
              class="required-field-star">*</span>
          </b>
          <multiselect
            v-model="dataInfo.resident.city.country"
            @close="$v.dataInfo.resident.city.country.$touch()"
            :searchable="true"
            :options="mappingCountry"
            :placeholder="$t('country')"
            :label="labelValue"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataInfo.resident.city.country.$dirty && !$v.dataInfo.resident.city.country.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="w-30">
          <b>
            {{ $t('region') }}
            <span v-if="dataInfo.country && dataInfo.country.id === 2"
              class="required-field-star">*</span>
          </b>
          <multiselect
            v-model="dataInfo.resident.city.region"
            @input="mappingCityList(dataInfo.resident.city.region, 'resident')"
            @close="$v.dataInfo.resident.city.region.$touch()"
            :searchable="true"
            :options="mappingRegion(dataInfo.resident.city.country)"
            :placeholder="$t('region')"
            :label="labelValue"
            track-by="id"
          >
            <span slot="noOptions">
              {{ $t('selectCountry') }}
            </span>
          </multiselect>
          <ValidationAlert
            v-if="$v.dataInfo.resident.city.region.$dirty && !$v.dataInfo.resident.city.region.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="w-40 p-0">
          <b>
            {{ $t('city') }}
            <span v-if="dataInfo.country && dataInfo.country.id === 2"
              class="required-field-star">*</span>
          </b>
          <multiselect
            v-model="dataInfo.resident.city.city"
            @close="$v.dataInfo.resident.city.city.$touch()"
            :searchable="true"
            :options="residentCitiesList"
            :placeholder="$t('city')"
            :label="labelValue"
            track-by="id"
          >
            <span slot="noOptions">
              {{ $t('selectRegion') }}
            </span>
          </multiselect>
          <ValidationAlert
            v-if="$v.dataInfo.resident.city.city.$dirty && !$v.dataInfo.resident.city.city.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div class="w-100 p-0 d-flex">
        <div class="w-20 p-0">
          <b>
            {{ $t('placeIndex') }}
            <span v-if="dataInfo.country && dataInfo.country.id === 2"
              class="required-field-star">*</span>
          </b>
          <b-input
            v-model="dataInfo.resident.index"
            @blur="$v.dataInfo.resident.index.$touch()"
            :placeholder="$t('placeIndex')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataInfo.resident.index.$dirty && !$v.dataInfo.resident.index.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataInfo.resident.index.$dirty &&
            (!$v.dataInfo.resident.index.maxLength || !$v.dataInfo.resident.index.minLength)"
            :text="$t('placeIndexCount')"
          />
        </div>
        <div class="w-50">
          <b>
            {{ $t('street') }}
            <span v-if="dataInfo.country && dataInfo.country.id === 2"
              class="required-field-star">*</span>
          </b>
          <b-input
            v-model="dataInfo.resident.street"
            @blur="$v.dataInfo.resident.street.$touch()"
            :placeholder="$t('street')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataInfo.resident.street.$dirty && !$v.dataInfo.resident.street.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="w-15 pl-0">
          <b>
            {{ $t('house') }}
            <span v-if="dataInfo.country && dataInfo.country.id === 2"
              class="required-field-star">*</span>
          </b>
          <b-input
            v-model="dataInfo.resident.house"
            @blur="$v.dataInfo.resident.house.$touch()"
            :placeholder="$t('house')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataInfo.resident.house.$dirty && !$v.dataInfo.resident.house.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="w-15 p-0">
          <b>{{ $t('flat') }}</b>
          <b-input
            v-model="dataInfo.resident.flat"
            :placeholder="$t('flat')"
            type="text"
          />
        </div>
      </div>
    </div>

    <div class="w-100 mt-3">
      <FileDropZone ref="mediaContent" />
    </div>
  </div>
</template>

<script src="./SailorCitizenPassportEdit.js"/>
