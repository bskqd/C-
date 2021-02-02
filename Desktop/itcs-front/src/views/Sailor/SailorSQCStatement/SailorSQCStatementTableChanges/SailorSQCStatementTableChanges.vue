<template>
  <v-dialog
    v-model="activeModal"
    max-width="700"
  >
    <template #activator="{ on, attrs }">
      <v-btn
        v-bind="attrs"
        v-on="on"
        style="outline: none"
        fab
        small
      >
        <v-icon>
          mdi-cog-transfer-outline
        </v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title class="headline">
        <v-tabs v-model="tabs">
          <v-tab>{{ $t('editing') }}</v-tab>
          <v-tab>{{ $t('addDocument') }}</v-tab>
        </v-tabs>
      </v-card-title>

      <v-card-text class="p-1">
        <v-tabs-items v-model="tabs">
          <v-tab-item>
            <v-select
              v-model="documentFrom"
              @input="documentTo = null"
              @blur="$v.documentFrom.$touch()"
              :items="sailorDocument.status_dkk.exists_docs"
              :item-text="item => item.type_doc + ' - ' + item.number + ' ' + item.info"
              :label="$t('changeDocFrom')"
              :error-messages="documentFromErrors"
              class="mt-1"
              return-object
              clearable
            />
            <v-select
              v-model="documentTo"
              @blur="$v.documentTo.$touch()"
              :items="mappingDocumentsList(documentFrom)"
              :label="$t('changeDocTo')"
              :item-text="customDocumentLabel"
              :error-messages="documentToErrors"
              :disabled="!documentFrom"
              return-object
              clearable
            />
          </v-tab-item>

          <v-tab-item>
            <v-select
              v-model="contentType"
              @input="newDocument = null"
              :items="contentTypesList"
              :label="$t('typeDoc')"
              :item-text="labelName"
              return-object
              clearable
            />

            <v-select
              v-model="newDocument"
              @blur="$v.newDocument.$touch()"
              :items="mappingDocumentsList(contentType)"
              :label="$t('addDocument')"
              :item-text="customDocumentLabel"
              :error-messages="newDocumentErrors"
              :disabled="!contentType"
              return-object
              clearable
            />
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          @click="activeModal = false"
          color="darken-1"
          text
        >
          {{ $t('setReject') }}
        </v-btn>
        <v-btn
          @click="checkFieldsEntries"
          color="success"
        >
          {{ $t('save') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script src="./SailorSQCStatementTableChanges.js" />
