<template>
  <b-card header-tag="header">
    <b-form @submit.prevent="checkEditedDocument" class="text-left">
      <div
        v-if="sailorDocument.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'"
        class="seafarerInfoList"
      >
        <div class="w-50">
          <label>
            {{ $t('responsibility') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="sailorDocument.responsibility_work_book"
            @close="$v.sailorDocument.responsibility_work_book.$touch()"
            :options="mappingResponsibilityWorkBook"
            :searchable="true"
            :placeholder="$t('responsibility')"
            :label="labelName"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.responsibility_work_book.$dirty && !$v.sailorDocument.responsibility_work_book.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="w-50">
          <label>
            {{ $t('workPlace') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.place_work"
            @blur="$v.sailorDocument.place_work.$touch()"
            :placeholder="$t('workPlace')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.place_work.$dirty && !$v.sailorDocument.place_work.required"
            :text="$t('emptyField')"
          />
        </div>

        <div class="w-33">
          <label>
            {{ $t('periodStart') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input-group>
            <b-form-input
              v-model="sailorDocument.date_start"
              @blur="$v.dateStartObject.$touch()"
              :readonly="Boolean(sailorDocument.days_work)"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="sailorDocument.date_start"
                @hidden="$v.dateStartObject.$touch()"
                :disabled="Boolean(sailorDocument.days_work)"
                :locale="lang"
                :max="sailorDocument.date_end"
                min="1900-01-01"
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
            v-else-if="$v.dateStartObject.$dirty && (!$v.dateStartObject.minValue || !$v.dateStartObject.maxValue)"
            :text="$t('invalidDataFormat')"
          />
        </div>
        <div class="w-33">
          <label>
            {{ $t('periodEnd') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input-group>
            <b-form-input
              v-model="sailorDocument.date_end"
              @blur="$v.dateEndObject.$touch()"
              :readonly="Boolean(sailorDocument.days_work)"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="sailorDocument.date_end"
                @hidden="$v.dateEndObject.$touch()"
                :disabled="Boolean(sailorDocument.days_work)"
                :locale="lang"
                :max="new Date()"
                :min="sailorDocument.date_start"
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
            v-else-if="$v.dateEndObject.$dirty && (!$v.dateEndObject.minValue || !$v.dateEndObject.maxValue)"
            :text="$t('invalidDataFormat')"
          />
        </div>
        <div class="w-33">
          <label>
            {{ $t('totalDays') }}
            <span class="required-field-star">*</span>
          </label>
          <b-form-input
            v-model="sailorDocument.days_work"
            @blur="$v.sailorDocument.days_work.$touch()"
            :readonly="Boolean(sailorDocument.date_end || sailorDocument.date_start)"
            :placeholder="$t('totalDays')"
            type="number"
          />
        </div>

        <div class="w-100">
          <label>
            {{ $t('bookPractical') }}
          </label>
          <div class="d-flex justify-content-start align-items-center">
            <b-form-checkbox
              v-model="sailorDocument.book_registration_practical"
              name="bookPractical"
              class="mx-1"
              switch
            />
            <div v-if="sailorDocument.book_registration_practical">
              {{ $t('present') }}
            </div>
            <div v-else>
              {{ $t('missingFemale') }}
            </div>
          </div>
        </div>
      </div>

      <div
        v-else
        class="seafarerInfoList"
      >
        <div class="p-0">
          <h5 class="text-bold-600">
            {{ $t('infoShip') }}:
          </h5>
        </div>
        <div class="w-33">
          <label>
            {{ $t('numShip') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.number_vessel"
            @blur="$v.sailorDocument.number_vessel.$touch()"
            :placeholder="$t('numShip')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.number_vessel.$dirty && !$v.sailorDocument.number_vessel.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.sailorDocument.number_vessel.$dirty && !$v.sailorDocument.number_vessel.maxLength"
            :text="$t('tooLongNumber')"
          />
        </div>
        <div class="w-33">
          <label>
            {{ $t('nameShip') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.name_vessel"
            @blur="$v.sailorDocument.name_vessel.$touch()"
            :placeholder="$t('nameShip')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.name_vessel.$dirty && !$v.sailorDocument.name_vessel.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.sailorDocument.name_vessel.$dirty && !$v.sailorDocument.name_vessel.maxLength"
            :text="$t('shipNameLength')"
          />
        </div>
        <div class="w-33">
          <label>
            {{ $t('typeShip') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="sailorDocument.type_vessel"
            :options="mappingTypeShip"
            :searchable="true"
            :allow-empty="false"
            :placeholder="$t('typeShip')"
            :label="labelName"
            track-by="id"
          />
        </div>
        <div class="w-50">
          <label>
            {{ $t('modeShipping') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="sailorDocument.mode_of_navigation"
            :options="mappingModeShipping"
            :allow-empty="false"
            :searchable="true"
            :placeholder="$t('modeShipping')"
            :label="labelName"
            track-by="id"
          />
        </div>
        <div class="w-50">
          <label>
            {{ $t('portShip') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.port_of_registration"
            @blur="$v.sailorDocument.port_of_registration.$touch()"
            :placeholder="$t('portShip')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.port_of_registration.$dirty && !$v.sailorDocument.port_of_registration.required"
            :text="$t('emptyField')"
          />
        </div>
        <div>
          <label>
            {{ $t('ownerShip') }}
          </label>
          <b-input
            v-model="sailorDocument.ship_owner"
            @blur="$v.sailorDocument.ship_owner.$touch()"
            :placeholder="$t('ownerShip')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.ship_owner.$dirty && !$v.sailorDocument.ship_owner.maxLength"
            :text="$t('tooLongCaptName')"
          />
        </div>
        <div class="w-25">
          <label>
            {{ $t('grossCapacity') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.gross_capacity"
            @blur="$v.sailorDocument.gross_capacity.$touch()"
            :placeholder="$t('grossCapacity')"
            type="number"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.gross_capacity.$dirty && !$v.sailorDocument.gross_capacity.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.sailorDocument.gross_capacity.$dirty && !$v.sailorDocument.gross_capacity.numeric"
            :text="$t('onlyNumeric')"
          />
        </div>
        <div class="w-25">
          <label>
            {{ $t('powerGEU') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.propulsion_power"
            @blur="$v.sailorDocument.propulsion_power.$touch()"
            :placeholder="$t('powerGEU')"
            type="number"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.propulsion_power.$dirty && !$v.sailorDocument.propulsion_power.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.sailorDocument.propulsion_power.$dirty && !$v.sailorDocument.propulsion_power.numeric"
            :text="$t('onlyNumeric')"
          />
        </div>
        <div class="w-25">
          <label>{{ $t('coldProductivity') }}</label>
          <b-input
            v-model="sailorDocument.refrigerating_power"
            @blur="$v.sailorDocument.refrigerating_power.$touch()"
            :placeholder="$t('coldProductivity')"
            type="number"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.refrigerating_power.$dirty && !$v.sailorDocument.refrigerating_power.numeric"
            :text="$t('onlyNumeric')"
          />
        </div>
        <div class="w-25">
          <label>
            {{ $t('elEquipmentPower') }}
          </label>
          <b-input
            v-model="sailorDocument.electrical_power"
            @blur="$v.sailorDocument.electrical_power.$touch()"
            :placeholder="$t('elEquipmentPower')"
            type="number"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.electrical_power.$dirty && !$v.sailorDocument.electrical_power.numeric"
            :text="$t('onlyNumeric')"
          />
        </div>

        <div class="w-33">
          <label>
            {{ $t('typeGEU') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="sailorDocument.type_geu"
            :options="mappingTypeGEU"
            :allow-empty="false"
            :searchable="true"
            :placeholder="$t('typeGEU')"
            :label="labelName"
            track-by="id"
          />
        </div>
        <div class="w-33">
          <label>
            {{ $t('levelRefrigerantPlant') }}
          </label>
          <div class="flex-row-se">
            <b-form-checkbox
              v-model="sailorDocument.levelRefrigerPlant"
              name="levelRefrigerantPlant"
              value="1"
            >
              1
            </b-form-checkbox>
            <b-form-checkbox
              v-model="sailorDocument.levelRefrigerPlant"
              name="levelRefrigerantPlant"
              value="2"
            >
              2
            </b-form-checkbox>
          </div>
        </div>
        <div class="w-33">
          <label>
            {{ $t('apparatusGMZLB') }}
          </label>
          <div class="d-flex justify-content-center align-items-center">
            <b-form-checkbox
              v-model="sailorDocument.equipment_gmzlb"
              name="aparatusGMLZB"
              class="mx-1"
              switch
            />
            <div v-if="sailorDocument.equipment_gmzlb">
              {{ $t('present') }}
            </div>
            <div v-else>
              {{ $t('missingFemale') }}
            </div>
          </div>
        </div>
        <div class="w-50">
          <label>
            {{ $t('swimArea') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.trading_area"
            @blur="$v.sailorDocument.trading_area.$touch()"
            :placeholder="$t('swimArea')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.trading_area.$dirty && !$v.sailorDocument.trading_area.required"
            :text="$t('emptyField')"
          />
        </div>
        <div class="w-50">
          <label>
            {{ $t('swimPorts') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.ports_input"
            @blur="$v.sailorDocument.ports_input.$touch()"
            :placeholder="$t('swimPorts')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.ports_input.$dirty && !$v.sailorDocument.ports_input.required"
            :text="$t('emptyField')"
          />
        </div>

        <h5 class="text-bold-600 mt-2">
          {{ $t('captain') }}:
        </h5>

        <div>
          <label>{{ $t('fullNameUa') }}</label>
          <b-input
            v-model="sailorDocument.full_name_master"
            @blur="$v.sailorDocument.full_name_master.$touch()"
            :placeholder="$t('lastNameUK')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.full_name_master.$dirty && !$v.sailorDocument.full_name_master.alphaUA"
            :text="$t('noAlphaUA')"
          />
        </div>
        <div class="mt-2">
          <label>
            {{ $t('fullNameEn') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.full_name_master_eng"
            @blur="$v.sailorDocument.full_name_master_eng.$touch()"
            :placeholder="$t('lastNameEN')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.full_name_master_eng.$dirty && !$v.sailorDocument.full_name_master_eng.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.sailorDocument.full_name_master_eng.$dirty && !$v.sailorDocument.full_name_master_eng.alphaEN"
            :text="$t('noAlpha')"
          />
        </div>

        <div class="p-0 mt-2">
          <h5 class="text-bold-600">
            {{ $t('experience') }}:
          </h5>
        </div>

        <div>
          <label>
            {{ $t('bookPractical') }}
          </label>
          <div class="d-flex justify-content-start align-items-center">
            <b-form-checkbox
              v-model="sailorDocument.book_registration_practical"
              name="bookPractical"
              class="mx-1"
              switch
            />
            <div v-if="sailorDocument.book_registration_practical">
              {{ $t('present') }}
            </div>
            <div v-else>
              {{ $t('missingFemale') }}
            </div>
          </div>
        </div>
        <div class="w-50">
          <label>
            {{ $t('hirePlace') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.place_start"
            @blur="$v.sailorDocument.place_start.$touch()"
            :placeholder="$t('hirePlace')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.place_start.$dirty && !$v.sailorDocument.place_start.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.sailorDocument.place_start.$dirty && !$v.sailorDocument.place_start.maxLength"
            :text="$t('tooLongPlace')"
          />
        </div>
        <div class="w-50">
          <label>
            {{ $t('hireDate') }}
            <span class="required-field-star">*</span>
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
                :max="sailorDocument.date_end"
                min="1900-01-01"
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
            v-else-if="$v.dateStartObject.$dirty && (!$v.dateStartObject.minValue || !$v.dateStartObject.maxValue)"
            :text="$t('invalidDataFormat')"
          />
        </div>
        <div class="w-50">
          <label>
            {{ $t('firePlace') }}
            <span class="required-field-star">*</span>
          </label>
          <b-input
            v-model="sailorDocument.place_end"
            @blur="$v.sailorDocument.place_end.$touch()"
            :placeholder="$t('firePlace')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.sailorDocument.place_end.$dirty && !$v.sailorDocument.place_end.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.sailorDocument.place_end.$dirty && !$v.sailorDocument.place_end.maxLength"
            :text="$t('tooLongPlace')"
          />
        </div>
        <div class="w-50">
          <label>
            {{ $t('fireDate') }}
            <span class="required-field-star">*</span>
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
                :min="sailorDocument.date_start"
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
            v-else-if="$v.dateEndObject.$dirty && (!$v.dateEndObject.minValue || !$v.dateEndObject.maxValue)"
            :text="$t('invalidDataFormat')"
          />
        </div>

        <h5 class="text-bold-600 mt-2">
          {{ $t('repairedShip') }}:
        </h5>

        <div class="w-100">
          <div class="d-flex justify-content-start align-items-center">
            <b-form-checkbox
              v-model="sailorDocument.is_repaired"
              name="bookPractical"
              class="mx-1"
              switch
            />
            <div v-if="sailorDocument.is_repaired">
              {{ $t('yes') }}
            </div>
            <div v-else>
              {{ $t('no') }}
            </div>
          </div>
        </div>

        <div
          v-if="sailorDocument.is_repaired"
          class="w-100 d-flex text-left"
        >
          <div class="w-30 pl-0">
            <label>
              {{ $t('periodStart') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input-group>
              <b-form-input
                v-model="sailorDocument.repair_date_from"
                @input="displayDateInputs('repairing')"
                @blur="$v.sailorDocument.repair_date_from.$touch()"
                :readonly="readonlyInputs"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="sailorDocument.repair_date_from"
                  @input="displayDateInputs('repairing')"
                  @hidden="$v.sailorDocument.repair_date_from.$touch()"
                  :disabled="readonlyInputs"
                  :locale="lang"
                  :max="sailorDocument.date_end"
                  :min="sailorDocument.date_start"
                  start-weekday="1"
                  button-only
                  right
                />
              </b-input-group-append>
            </b-input-group>
            <ValidationAlert
              v-if="$v.sailorDocument.repair_date_from.$dirty && !$v.sailorDocument.repair_date_from.required"
              :text="$t('emptyField')"
            />
          </div>
          <div class="w-30">
            <label>
              {{ $t('periodEnd') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input-group>
              <b-form-input
                v-model="sailorDocument.repair_date_to"
                @input="displayDateInputs('repairing')"
                @blur="$v.sailorDocument.repair_date_to.$touch()"
                :readonly="readonlyInputs"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="sailorDocument.repair_date_to"
                  @input="displayDateInputs('repairing')"
                  @hidden="$v.sailorDocument.repair_date_to.$touch()"
                  :disabled="readonlyInputs"
                  :locale="lang"
                  :max="sailorDocument.date_end"
                  :min="sailorDocument.date_start"
                  start-weekday="1"
                  button-only
                  right
                />
              </b-input-group-append>
            </b-input-group>
            <ValidationAlert
              v-if="$v.sailorDocument.repair_date_to.$dirty && !$v.sailorDocument.repair_date_to.required"
              :text="$t('emptyField')"
            />
          </div>
          <div class="w-10 d-flex justify-content-center align-items-center">
            <label>{{ $t('or') }}</label>
          </div>
          <div class="w-30 pr-0">
            <label>
              {{ $t('totalDays') }}
              <span class="required-field-star">*</span>
            </label>
            <b-form-input
              v-model="sailorDocument.days_repair"
              @input="displayDateInputs('repairing')"
              @blur="$v.sailorDocument.days_repair.$touch()"
              :readonly="readonlyDateNum"
              :placeholder="$t('totalDays')"
              type="number"
            />
            <ValidationAlert
              v-if="$v.sailorDocument.days_repair.$dirty && !$v.sailorDocument.days_repair.required"
              :text="$t('emptyField')"
            />
          </div>
        </div>

        <div class="p-0 mt-2">
          <h5 class="text-bold-600">
            {{ $t('responsibility') }}:
          </h5>
        </div>

        <div class="w-50 text-left">
          <label class="w-100">
            {{ $t('responsibility') }}
          </label>
          <div class="d-flex w-100">
            <multiselect
              v-model="responsibility"
              @input="addResponsibility(responsibility)"
              :options="mappingResponsibility"
              :searchable="true"
              :placeholder="$t('responsibility')"
              :label="labelName"
              track-by="id"
            />
            <unicon
              @click="addResponsibility(responsibility)"
              name="plus"
              height="30px"
              width="30px"
              class="cursor add"
            />
          </div>
        </div>
        <div class="w-50">
          <label>
            {{ $t('positionOnShip') }}
            <span class="required-field-star">*</span>
          </label>
          <multiselect
            v-model="sailorDocument.position"
            :options="mappingPositionsShip"
            :allow-empty="false"
            :searchable="true"
            :placeholder="$t('positionOnShip')"
            :label="labelName"
            track-by="id"
          />
        </div>

        <div class="w-100">
          <div
            v-for="(resp, index) of sailorDocument.all_responsibility"
            :key="resp.id"
            class="w-100 text-left p-0 m-0"
          >
            <div
              v-if="resp.responsibility"
              class="pl-0"
            >
              <label>{{ resp.responsibility[labelName] }}:</label>
              <unicon
                @click="deleteResponsibility(index)"
                name="multiply"
                fill="#42627e"
                height="20px"
                width="20px"
                class="close"
              />
            </div>
            <div
              v-if="resp.responsibility"
              class="w-100 pl-0 pr-0 d-flex mb-1"
            >
              <div class="w-30">
                <label>
                  {{ $t('periodStart') }}
                  <span class="required-field-star">*</span>
                </label>
                <b-input-group>
                  <b-form-input
                    v-model="sailorDocument.all_responsibility[index].date_from"
                    @input="displayDateInputs('responsibility')"
                    @blur="$v.sailorDocument.all_responsibility.$each[index].date_from.$touch()"
                    :readonly="readonlyInputs"
                    type="date"
                  />
                  <b-input-group-append>
                    <b-form-datepicker
                      v-model="sailorDocument.all_responsibility[index].date_from"
                      @input="displayDateInputs('responsibility')"
                      @hidden="$v.sailorDocument.all_responsibility.$each[index].date_from.$touch()"
                      :disabled="readonlyInputs"
                      :locale="lang"
                      :max="sailorDocument.date_end"
                      :min="sailorDocument.date_start"
                      start-weekday="1"
                      button-only
                      right
                    />
                  </b-input-group-append>
                </b-input-group>
                <ValidationAlert
                  v-if="$v.sailorDocument.all_responsibility.$each[index].date_from.$dirty &&
                     !$v.sailorDocument.all_responsibility.$each[index].date_from.required"
                  :text="$t('emptyField')"
                />
                <!--<ValidationAlert
                  v-else-if="$v.sailorDocument.all_responsibility.$each[index].date_from.$dirty &&
                     (!$v.sailorDocument.all_responsibility.$each[index].date_from.maxValue ||
                      !$v.sailorDocument.all_responsibility.$each[index].date_from.minValue)"
                  :text="$t('invalidDataFormat')"
                />-->
              </div>
              <div class="w-30">
                <label>
                  {{ $t('periodEnd') }}
                  <span class="required-field-star">*</span>
                </label>
                <b-input-group>
                  <b-form-input
                    v-model="sailorDocument.all_responsibility[index].date_to"
                    @input="displayDateInputs('responsibility')"
                    @blur="$v.sailorDocument.all_responsibility.$each[index].date_to.$touch()"
                    :readonly="readonlyInputs"
                    type="date"
                  />
                  <b-input-group-append>
                    <b-form-datepicker
                      v-model="sailorDocument.all_responsibility[index].date_to"
                      @input="displayDateInputs('responsibility')"
                      @hidden="$v.sailorDocument.all_responsibility.$each[index].date_to.$touch()"
                      :disabled="readonlyInputs"
                      :locale="lang"
                      :max="sailorDocument.date_end"
                      :min="sailorDocument.date_start"
                      start-weekday="1"
                      button-only
                      right
                    />
                  </b-input-group-append>
                </b-input-group>
                <ValidationAlert
                  v-if="$v.sailorDocument.all_responsibility.$each[index].date_to.$dirty &&
                     !$v.sailorDocument.all_responsibility.$each[index].date_to.required"
                  :text="$t('emptyField')"
                />
                <!--<ValidationAlert
                  v-else-if="$v.sailorDocument.all_responsibility.$each[index].date_to.$dirty &&
                     (!$v.sailorDocument.all_responsibility.$each[index].date_to.maxValue ||
                      !$v.sailorDocument.all_responsibility.$each[index].date_to.minValue)"
                  :text="$t('invalidDataFormat')"
                />-->
              </div>
              <div class="w-10 d-flex justify-content-center align-items-center">
                <label>{{ $t('or') }}</label>
              </div>
              <div class="w-30">
                <label>
                  {{ $t('totalDays') }}
                  <span class="required-field-star">*</span>
                </label>
                <b-form-input
                  v-model="sailorDocument.all_responsibility[index].days_work"
                  @input="displayDateInputs('responsibility')"
                  @blur="$v.sailorDocument.all_responsibility.$each[index].days_work.$touch()"
                  :readonly="readonlyDateNum"
                  :placeholder="$t('totalDays')"
                  type="number"
                />
                <ValidationAlert
                  v-if="$v.sailorDocument.all_responsibility.$each[index].days_work.$dirty &&
                     !$v.sailorDocument.all_responsibility.$each[index].days_work.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="p-0">
          <h5 class="text-bold-600 text-left mt-1 mb-0">
            {{ $t('photoOrPDF') }}:
          </h5>
        </div>
      </div>

      <FileDropZone ref="mediaContent" class="w-100 p-2" />
      <div>
        <b-overlay
          :show="buttonLoader"
          spinner-variant="primary"
          opacity="0.65"
          blur="2px"
          variant="white"
          class="w-100 mt-1 text-center"
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
    </b-form>
  </b-card>
</template>

<script src="./SailorExperienceEdit.js"/>
