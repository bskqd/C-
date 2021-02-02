<template>
  <b-card header-tag="header">
    <b-form @submit.prevent="checkEditedDoc">
      <div class="seafarerInfoList">
        <!--Possibility to edit Strict blank if status is "Processing" for DPO-->
        <div v-if="checkAccess('qualification', 'editStrictBlank', sailorDocument)">
          <b>{{ $t('strictBlank')}}</b>
          <b-input
            v-model="sailorDocument.strict_blank"
            :placeholder="$t('strictBlank')"
            type="text"
          />
        </div>
        <div
          v-if="checkAccess('qualification', 'edit', sailorDocument)"
          class="seafarerInfoList p-0"
        >
          <!--typeId = 16 - Підтвердження робочого диплому-->
          <div
            v-if="sailorDocument.type_document.id !== 16 && !sailorDocument.other_number"
            class="w-100"
          >
            <b>{{ $t('number') }}:</b>
            <b-input
              v-model="sailorDocument.number_document"
              @blur="$v.sailorDocument.number_document.$touch()"
              :placeholder="$t('number')"
              type="text"
            />
            <ValidationAlert
              v-if="$v.sailorDocument.number_document.$dirty && !$v.sailorDocument.number_document.required"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="$v.sailorDocument.number_document.$dirty && !$v.sailorDocument.number_document.maxLength"
              :text="$t('tooLongNumDoc')"
            />
          </div>
          <div
            v-else-if="sailorDocument.other_number"
            class="w-100"
          >
            <b>{{ $t('number') }}:</b>
            <b-input
              v-model="sailorDocument.other_number"
              @blur="$v.sailorDocument.other_number.$touch()"
              :placeholder="$t('number')"
              type="text"
            />
            <ValidationAlert
              v-if="$v.sailorDocument.other_number.$dirty && !$v.sailorDocument.other_number.required"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="$v.sailorDocument.other_number.$dirty && !$v.sailorDocument.other_number.maxLength"
              :text="$t('tooLongNumDoc')"
            />
          </div>

          <div class="w-50 p-0">
            <div class="w-25 text-left">
              <b>{{ $t('port') }}:</b>
            </div>
            <div
              v-if="!sailorDocument.other_port"
              class="w-100 text-left"
            >
              <multiselect
                v-model="sailorDocument.port"
                :options="ports"
                :allow-empty="false"
                :searchable="true"
                :placeholder="$t('port')"
                :label="labelName"
                track-by="id"
              />
            </div>
            <div
              v-else
              class="w-100 text-left"
            >
              <b-input
                v-model="sailorDocument.other_port"
                @blur="$v.sailorDocument.other_port.$touch()"
                :placeholder="$t('port')"
                type="text"
              />
              <ValidationAlert
                v-if="$v.sailorDocument.other_port.$dirty && !$v.sailorDocument.other_port.required"
                :text="$t('emptyField')"
              />
            </div>
          </div>

          <div
            v-if="sailorDocument.type_document.id !== 16"
            class="w-50"
          >
            <b>{{ $t('rank') }}:</b>
            <multiselect
              v-model="sailorDocument.rank"
              @input="clearPosition(sailorDocument.rank, sailorDocument.list_positions)"
              :options="ranks"
              :allow-empty="false"
              :searchable="true"
              :placeholder="$t('rank')"
              :label="labelName"
              track-by="id"
            />
          </div>
          <div
            v-if="sailorDocument.type_document.id !== 16"
            class="w-50"
          >
            <b>{{ $t('position') }}:</b>
            <multiselect
              v-model="sailorDocument.list_positions"
              :options="mappingPositions(sailorDocument.rank)"
              :searchable="true"
              :placeholder="$t('position')"
              :allow-empty="false"
              :label="labelName"
              track-by="id"
              multiple
            />
            <ValidationAlert
              v-if="$v.sailorDocument.list_positions.$dirty && !$v.sailorDocument.list_positions.required"
              :text="$t('emptyField')"
            />
          </div>
          <div class="w-50">
            <b>{{ $t('dateIssue') }}:</b>
            <b-input-group>
              <b-form-input
                v-model="sailorDocument.date_start"
                @blur="$v.dateStartObject.$touch()"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="sailorDocument.date_start"
                  @input="$v.dateStartObject.$touch()"
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
              v-if="$v.dateStartObject.$dirty && !$v.dateStartObject.required"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="$v.dateStartObject.$dirty &&
                (!$v.dateStartObject.maxValue || !$v.dateStartObject.minValue)"
              :text="$t('dateIssuedValid')"
            />
          </div>
          <div
            v-if="sailorDocument.date_end"
            class="w-50"
          >
            <b>{{ $t('dateEnd') }}:</b>
            <b-input-group>
              <b-form-input
                v-model="sailorDocument.date_end"
                @blur="$v.dateEndObject.$touch()"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="sailorDocument.date_end"
                  @inpet="$v.dateEndObject.$touch()"
                  :locale="lang"
                  :min="dateStartObject"
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
              v-else-if="$v.dateEndObject.$dirty &&
                (!$v.dateEndObject.maxValue || !$v.dateEndObject.minValue)"
              :text="$t('dateTerminateValid')"
            />
          </div>
            <div>
              <FileDropZone ref="mediaContent" class="w-100 p-0" />
            </div>
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

<script src="./SailorQualificationEdit.js"/>
