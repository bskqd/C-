<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList text-left">
      <div class="seafarerInfoList">
        <b-button
          @click="saveDocument(sailorDocument)"
          class="text-bold-600 m-0"
        >
          {{ $t('saveDoc') }}
        </b-button>

        <div class="w-100 p-0 mt-1">
          <b>{{ $t('number') }}:</b>
          {{ sailorDocument.number }}
        </div>

        <div class="w-50 p-0 mt-1">
          <b>{{ $t('rank') }}:</b>
          {{ sailorDocument.rank[labelName] }}
        </div>

        <div class="w-50 mt-1">
          <b>{{ $t('position') }}:</b>
          <span v-for="position in sailorDocument.list_positions" :key="position.id">{{ position[labelName] }};</span>
        </div>

        <div
          v-if="sailorDocument.date_meeting"
          class="w-100 mt-1 px-3"
        >
          <b>{{ $t('dataEvent') }}:</b>
          {{ getDateFormat(sailorDocument.date_meeting) }}
        </div>
      </div>

      <div class="w-100">
        <label class="text-bold-600">
          {{ $t('existsDocs') }}:
        </label>
      </div>
      <b-table
        :items="sailorDocument.status_dkk.exists_docs"
        :fields="fieldsExistDocuments"
        :sort-by.sync="sortByA"
        :sort-desc.sync="sortDescA"
        striped
        hover
      >
        <template #cell(status)="row">
          <span :class="getStatus(row.item.is_verification ? 34 : 1)">
            {{ row.item.is_verification ? $t('notVerified') : $t('verified') }}
          </span>
        </template>

        <template #cell(date_start)="row">
          {{ getDateFormat(row.item.date_start) }}
        </template>

        <template #cell(date_end)="row">
          {{ getDateFormat(row.item.date_end) }}
        </template>
      </b-table>

      <div class="mt-1">
        <label class="text-bold-600">
          {{ $t('notExistsDocs') }}:
        </label>
      </div>
      <b-table
        :items="sailorDocument.status_dkk.documents"
        :fields="fieldsApplication"
        :sort-by.sync="sortByA"
        :sort-desc.sync="sortDescA"
        striped
        hover
      />

      <div
        v-if="checkAccess('qualificationStatement', 'viewExperienceTable')"
        class="mt-1"
      >
        <label class="text-bold-600">
          {{ $t('experience') }}: {{ $t('noCheck') }}
        </label>
      </div>
      <b-table
        :items="sailorDocument.status_dkk.experince"
        :fields="fieldsExperience"
        :sort-by.sync="sortByA"
        :sort-desc.sync="sortDescA"
        striped
        hover
      >
        <template #cell(status)="row">
          <div
            class="experience-status"
            :class="getStatus(row.item.value ? 1 : 7)"
          >
            {{ getExperienceStatus(row) }}
          </div>
        </template>
      </b-table>

      <div>
        <b>{{ $t('protocolSQC') }}:</b>
        <span v-if="sailorDocument.protocol_dkk">
          {{ sailorDocument.protocol_dkk.number }} /
          <span v-for="position of sailorDocument.protocol_dkk.position" :key="position.id">
            {{ position[labelName] }}
          </span>
        </span>
        <span v-if="sailorDocument.protocol_dkk">
          <router-link :to="{ name: 'sqc-protocols-info', params: { documentID: sailorDocument.protocol_dkk.id }}">
            ({{ $t('openProtocol') }})
          </router-link>
        </span>
        <span v-else>
          {{ $t('noProvided') }}
        </span>
      </div>

      <div v-if="checkAccess('admin')">
        <b>{{ $t('typeDoc') }}:</b>
        <span v-if="sailorDocument.is_continue">{{ $t('confirmation') }}</span>
        <span v-else>{{ $t('appropriation') }}</span>
      </div>

      <div>
        <b>{{ $t('payment') }}:</b>
        {{ sailorDocument.is_payed ? $t('isPayed') : $t('notPayed')  }}
      </div>

      <div>
        <b>{{ $t('status') }}:</b>
        <span :class="getStatus(sailorDocument.status_document.id)">
          {{ sailorDocument.status_document[labelName] }}
        </span>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorQualificationStatementInfo.js"/>
