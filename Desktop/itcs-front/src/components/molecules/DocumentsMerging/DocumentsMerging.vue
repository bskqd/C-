<template>
  <div>
    <div class="w-100 d-flex align-items-center mt-6">
      <v-card
        v-if="documentFrom"
        elevation="0"
        class="w-50 mr-3"
      >
        <v-card-title>{{ $t('fromDocument') }}:</v-card-title>
        <SailorEducationInfo
          v-if="type === 'education'"
          :sailorDocument="documentFrom"
        />
        <SailorQualificationInfo
          v-else
          :sailorDocument="documentFrom"
        />
      </v-card>

      <v-icon color="blue" x-large>mdi-arrow-right-circle-outline</v-icon>

      <v-card
        v-if="documentTo"
        elevation="0"
        class="w-50 ml-3"
      >
        <v-card-title>{{ $t('toDocument') }}:</v-card-title>
        <SailorEducationInfo
          v-if="type === 'education'"
          :sailorDocument="documentTo"
        />
        <SailorQualificationInfo
          v-else
          :sailorDocument="documentTo"
        />
      </v-card>
    </div>

    <div class="d-flex justify-content-center">
      <v-btn
        @click="mergeDocuments"
        color="success"
        elevation="2"
        class="mt-3"
      >
        {{ $t('save') }}
      </v-btn>
    </div>
  </div>
</template>

<script src="./DocumentsMerging.js" />
