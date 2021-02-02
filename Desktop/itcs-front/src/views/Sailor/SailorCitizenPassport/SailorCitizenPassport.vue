<template>
  <b-card>
    <b-overlay
      :show="cardLoader"
      spinner-variant="primary"
      opacity="0.65"
      blur="2px"
      variant="white"
    >
      <div class="d-flex p-2 align-items-flex-start">
        <div class="w-30">
          <ViewPhotoList
            v-if="Object.keys(this.item).length"
            :sailorDocument="item"
            documentType="civilPassport"
          />
        </div>
        <div class="w-70 seafarerInfoList justify-content-flex-start pl-10">
          <div
            v-if="checkAccess('civilPassport', 'edit')"
            class="d-flex justify-content-flex-end"
          >
            <unicon
              v-if="readonly"
              @click="readonly = !readonly"
              name="pen"
              fill="royalblue"
              class="mr-3"
            />

            <unicon
              v-if="!readonly"
              @click="checkInfo()"
              name="check"
              fill="limegreen"
              class="submit-edit-button mr-3"
              width="30"
              height="30"
            />

            <unicon
              v-if="!readonly"
              @click="finishEdit()"
              name="cancel"
              fill="royalblue"
              width="30"
              height="30"
            />
          </div>

          <SeafarerCitizenPassportInfo
            v-if="readonly"
            :data="item"
          />

          <SeafarerCitizenPassportEdit
            v-if="!readonly"
            :dataInfo="item"
            :finishEdit="finishEdit"
            ref="SeafarerCitizenPassEdit"
          />
        </div>
      </div>
    </b-overlay>
  </b-card>
</template>

<script src="./SailorCitizenPassport.js"/>

<style scoped>
  .active svg {
    fill: #42627e
  }
</style>
