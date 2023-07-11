const PromptsVertexIntegration = {
    props: ['selectedPrompt', 'isRunClicked'],
    components: {
        'prompts-range': PromptsRange,
    },
    data() {
        return {
            editableIntegrationSetting: {
                temperature: 0,
                max_decode_steps: 1,
                top_k: 1,
                top_p: 0,
                model_name: ""
            },
            isComponentMounted: false,
        }
    },
    computed: {
        responsiveTableHeight() {
            return `${(window.innerHeight - 270)}px`;
        },
        isInvalid() {
            return this.isRunClicked && !this.editableIntegrationSetting.model_name
        }
    },
    mounted() {
        if (this.selectedPrompt.model_settings) {
            this.editableIntegrationSetting = { ...this.selectedPrompt.model_settings };
            this.isComponentMounted = true;
        }
    },
    watch: {
        selectedPrompt: {
            handler: function (newVal, oldVal) {
                if (newVal.id === oldVal.id) return
                this.editableIntegrationSetting = { ...this.selectedPrompt.model_settings };
            },
            deep: true
        },
        editableIntegrationSetting: {
            handler: function (newVal, oldVal) {
                this.$emit('update-setting', newVal)
            },
            deep: true
        }
    },
    template: `
        <div>
            <div class="mt-4" v-if="isComponentMounted">
                <div class="form-group">
                    <p class="font-h5 font-semibold">Model</p>
                    <div class="custom-input custom-input__sm mb-3 mt-1" :class="{ 'invalid-input': isInvalid }">
                        <input type="text" placeholder="Model name" 
                        v-model="editableIntegrationSetting.model_name">
                        <span class="input_error-msg"></span>
                    </div>
                </div>
                <prompts-range
                    @register="$root.register"
                    instance_name="prompts-range"
                    title="temperature"
                    :step="0.05"
                    :minValue="0"
                    :maxValue="1"
                    v-model:modelValue="editableIntegrationSetting.temperature"
                ></prompts-range>
                <prompts-range
                    @register="$root.register"
                    instance_name="prompts-range"
                    title="Token limit"
                    :step="1"
                    :minValue="1"
                    :maxValue="1024"
                    v-model:modelValue="editableIntegrationSetting.max_decode_steps"
                ></prompts-range>
                <prompts-range
                    @register="$root.register"
                    instance_name="prompts-range"
                    title="Top-K"
                    :step="1"
                    :minValue="1"
                    :maxValue="40"
                    v-model:modelValue="editableIntegrationSetting.top_k"
                ></prompts-range>
                <prompts-range
                    @register="$root.register"
                    instance_name="prompts-range"
                    title="Top-P"
                    :step="0.05"
                    :minValue="0"
                    :maxValue="1"
                    v-model:modelValue="editableIntegrationSetting.top_p"
                ></prompts-range>
            </div>
        </div>
    `
}