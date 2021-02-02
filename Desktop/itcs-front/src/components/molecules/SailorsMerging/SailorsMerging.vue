<template>
  <div class="w-100 text-left">
    <v-btn
      @click.stop="showSailorsMerging = true"
      color="primary"
      outlined
    >
      {{ $t('accountMerging') }}
    </v-btn>
    <v-dialog
      v-model="showSailorsMerging"
      max-width="550"
    >
      <v-card>
        <v-card-title>{{ $t('accountMerging') }}</v-card-title>
        <v-card-text class="text-left">
          <div class="w-100">
            <label>{{ $t('sailorId') }}:</label>
            <v-text-field
              v-model="sailorID"
              :placeholder="$t('sailorId')"
              type="number"
              hide-details
              outlined
              dense
            />
          </div>
          <div
            v-if="availableSailor.length"
            class="w-100 mt-1 mb-3 text-secondary"
          >
            <p class="ma-0 pa-0">{{ $t('similarSailors') }}:</p>
            <p v-for="(sailor, index) of availableSailor" :key="index" class="ma-0 pa-0">
              <span @click="sailorID = sailor.sailor_id" class="cursor">
                - {{ sailor.sailor_id }} {{ sailor.full_name_ukr }} {{ sailor.date_birth }}
              </span>
              <router-link :to="{ name: 'passports-sailors', params: { id: sailor.sailor_id } }" target="_blank">
                ({{ $t('openSailor') }})
              </router-link>
            </p>
          </div>
          <div class="w-100 mt-1 mb-3">
            * {{ $t('sailorMergeTip') }}
          </div>
          <div class="w-100 d-flex justify-content-around">
            <v-btn
              @click="showSailorsMerging = false"
              depressed
            >
              {{ $t('setReject') }}
            </v-btn>
            <v-btn
              @click="mergeSailors"
              :disabled="!sailorID"
              color="success"
            >
              {{ $t('save') }}
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script src="./SailorsMerging.js" />
