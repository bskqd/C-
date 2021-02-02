<template>
  <v-stepper
    v-model="verificationStep"
    vertical
  >
    <div
      v-for="step in sailorDocument.verification_status"
      :key="step.order_number"
    >
      <v-stepper-step
        :complete="verificationStep > step.order_number"
        :step="step.order_number"
      >
        {{ step[labelName] }}
        <span v-if="verificationStep > step.order_number">
          <small
            v-for="(comment, index) in step.commments"
            :key="index"
          >
             - {{ comment.comment }} <br/>
          </small>
        </span>
      </v-stepper-step>

      <v-stepper-content
        :step="step.order_number"
        class="verificationStep-content"
      >
        <div
          v-for="comment in step.commments"
          :key="comment.id"
          class="verificationStep-comment"
        >
          <v-icon
            v-if="checkAccess('verification-comment')"
            @click="deleteComment(comment)"
            class="verificationStep-comment-delete"
          >
            mdi-close
          </v-icon>
          <v-card class="pa-1">
            {{ comment.comment }}
          </v-card>
          <div v-if="comment.author">
            <small>{{ comment.author.name }}</small>
            <small>{{ comment.author.date }}</small>
          </div>
        </div>

        <v-expansion-panels>
          <v-expansion-panel>
            <v-expansion-panel-header class="pa-0 px-3">
              {{ $t('setComment') }}
            </v-expansion-panel-header>
            <v-expansion-panel-content class="text-right">
              <v-textarea
                v-model="comment"
                :placeholder="$t('viewLastComment')"
                class="mt-5"
                height="80"
                outlined
              />
              <v-btn
                @click="setComment(step)"
                color="primary"
              >
                {{ $t('setComment') }}
              </v-btn>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>

        <div class="d-flex justify-space-around mt-3">
          <v-btn
            @click="setVerificationStatus"
            color="success"
          >
            {{ $t('nextVerificationStatus') }}
          </v-btn>
        </div>
      </v-stepper-content>
    </div>
  </v-stepper>
</template>

<script src="./VerificationSteps.js" />
