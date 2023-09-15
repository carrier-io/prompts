const PromptsAiDialIntegration = {
    props: ['selectedPrompt', 'isRunClicked'],
    components: {
        'prompts-range': PromptsRange,
    },
    data() {
        return {
            editableIntegrationSetting: {
                temperature: 0,
                model: "",
            },
            isComponentMounted: false,
            allModels: [],
            isModelsLoadung: false,
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
        this.$nextTick(() => {
            $('#selectModel').val(this.editableIntegrationSetting.model_name).selectpicker('refresh');
        })
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
                <div class="select-validation mt-4 mb-4" :class="{ 'invalid-input': isInvalid }">
                    <p class="font-h5 font-semibold mb-1">Select model</p>
                    <select id="selectModel" class="selectpicker bootstrap-select__b bootstrap-select__b-sm"
                        v-model="editableIntegrationSetting.model_name"
                        data-style="btn">
                        <option v-for="model in selectedPrompt.model_settings.models" :value="model">{{ model }}</option>
                    </select>
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
                    :maxValue="32000"
                    v-model:modelValue="editableIntegrationSetting.max_tokens"
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
