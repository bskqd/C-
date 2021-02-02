<template>
  <div class="w-100">
    <div v-if="row.documents_exists.length">
      <label class="pl-1 mt-1">{{ $t('existsDocs') }}:</label>
      <b-table
        :items="row.documents_exists"
        :fields="fieldsExistDocuments"
        class="text-center"
        striped
        hover
      >
        <template #cell(status)="row">
          <span :class="getStatus(row.item.is_verification ? 34 : 1)">
            {{ row.item.is_verification ? $t('notVerified') : $t('verified') }}
          </span>
        </template>
      </b-table>
    </div>

    <div v-if="row.documents_not_exists.length">
      <label class="pl-1 mt-1">{{ $t('notExistsDocs') }}:</label>
      <b-table
        :items="row.documents_not_exists"
        :fields="fieldsNotExistDocuments"
        class="text-center"
        striped
        hover
      />
    </div>

    <div v-if="row.experience.length">
      <label class="pl-1 mt-1">
        {{ $t('experience') }}
        <span v-if="row.used_verification_exp">({{ $t('usedVerificationExp') }})</span>:
      </label>
      <b-table
        :items="row.experience"
        :fields="fieldsExperience"
        class="text-center"
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
    </div>
  </div>
</template>

<script src="./SailorPositionStatementPreview.js" />

<style scoped>
  .experience-column {
    display: inline-block;
    width: auto !important;
  }
</style>
