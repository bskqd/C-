<template>
  <div style="margin-top: 6rem">
    <div class="flex-row-sb mb-1 col-12">
      <div>
        <label>
          {{ $t('webCam') }}
        </label>
      </div>
      <div>
        <unicon
          name="multiply"
          @click="closeWebCam"
          height="15px"
          width="15px"
          class="cursor delete"
        />
      </div>
    </div>

      <div v-if="detectWebCam">
        <div class="flex-row-sb mb-1 col-12">
        <multiselect
          v-model="activeCamera"
          @input="selectCamera(activeCamera)"
          :options="allCameras"
          :placeholder="$t('webCam')"
          :allow-empty="false"
          label="label"
          id="deviceId"
        />
      </div>

      <div class="flex-row-sb mb-1" style="height: 420px; overflow: hidden">
        <div class="col-7" style="height: 500px">
          <vue-web-cam
            :selectFirstDevice="true"
            :deviceId="activeCameraId"
            screenshotFormat="image/jpg"
            ref="webCam"
            class="camera"
          />
        </div>
        <div class="col-5" style="overflow-y: scroll; overflow-x: hidden; height: 100%; max-height: 500px;">
          <div
            :key="index"
            v-for="(scan, index) in scans"
            class="preview-photo--item"
            style="height: 300px; display: flex; flex-direction: column"
          >
            <img
              :src="scan.src"
              alt="scans"
              class="preview-photo"
            />
          </div>
        </div>
      </div>

      <div class="mb-1 col-12 text-left">
        <b-button
          @click="takePhoto"
          type="button"
        >
          {{ $t('makePhoto') }}
        </b-button>
      </div>

      <div class="mt-1 mb-1 col-12 text-left">
        <label>
          {{ $t('takenPhoto')}}:
        </label>
        <span
          :key="scan.file.name"
          v-for="(scan, index) in scans"
          class="mr-1"
        >
          {{ scan.file.name }}
          <unicon
            @click="deletePhotoScan(scan, index)"
            name="multiply"
            height="15px"
            width="15px"
            class="cursor delete"
          />;
        </span>
      </div>

      <div class="mt-1 mb-1">
        <b-button
          @click="usePhoto"
          type="button"
        >
          {{ $t('uploadDocs') }}
        </b-button>
      </div>
    </div>
    <div v-else>
      {{ $t('scannerNotDetect') }}
    </div>
  </div>
</template>

<script src="./WebCam.js"></script>

<style scoped></style>
