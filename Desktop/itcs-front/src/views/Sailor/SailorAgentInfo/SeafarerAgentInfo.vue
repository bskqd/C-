<template>
  <div class="vx-card p-2">
    <div class="d-flex wrap text-left">
      <div
        v-if="checkAccess('admin') && !agentName"
        class="w-100 text-right"
      >
        <unicon
          v-if="!agentEditing"
          @click="agentEditing = !agentEditing"
          name="pen"
          fill="#42627e"
          height="20px"
          width="20px"
          class="cursor"
        />
        <unicon
          v-else
          @click="agentEditing = !agentEditing"
          name="multiply"
          fill="#42627e"
          height="20px"
          width="20px"
          class="cursor"
        />
      </div>
      <div class="w-50 text-left">
        <label>{{ $t('userAgent') }}:</label>
        <div v-if="!agentEditing">
          <div v-if="agentName" class="d-flex align-items-center">
            {{ agentName }}
             <unicon
               v-if="checkAccess('backOffice')"
               @click="agentDeactivation"
               name="multiply"
               fill="#42627e"
               height="20px"
               width="20px"
               class="cursor ml-3"
             />
          </div>
        </div>
        <multiselect
          v-else
          v-model="agent"
          @search-change="startSearch"
          :searchable="true"
          :placeholder="$t('fullName')"
          :options="allAgents"
          label="fullName"
          track-by="id"
        >
          <template slot="noOptions">
            {{ $t('goSearch') }}
          </template>
          <template slot="noResult">
            <b-overlay
              :show="searchLoader"
              spinner-variant="primary"
              opacity="0.65"
              blur="2px"
              class="w-100"
              variant="white"
              spinner-small
            >
              {{ $t('emptySearchResult') }}
            </b-overlay>
          </template>
        </multiselect>
        <ValidationAlert
          v-if="$v.agent.$dirty && !$v.agent.required && agentEditing"
          :text="$t('emptyField')"
        />
      </div>
      <div v-if="agentEditing" class="w-50">
        <label>
          {{ $t('contractDateEnd') }}:
        </label>
        <b-input-group>
          <b-form-input
            v-model="contractDateEnd"
            @blur="$v.dateEndObject.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="contractDateEnd"
              @hidden="$v.dateEndObject.$touch()"
              :locale="lang"
              :min="new Date()"
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
          v-if="agentEditing"
          @click="checkFields"
          class="mt-1"
          type="submit"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </div>
</template>

<script src="./SeafarerAgentInfo.js" />
