/*******************************************************************************

 name:             CompressorPlugin
 version:          1.0.0
 vendor:           JUCE
 website:          https://oshe.io
 description:      compressor audio plugin.
 lastUpdated:	   March 17 2025 by Anna Andres

 dependencies:     juce_audio_basics, juce_audio_devices, juce_audio_formats,
                   juce_audio_plugin_client, juce_audio_processors, juce_dsp,
                   juce_audio_utils, juce_core, juce_data_structures,
                   juce_events, juce_graphics, juce_gui_basics, juce_gui_extra
 exporters:        linux makefile

 type:             AudioProcessor
 mainClass:        CompressorProcessor

*******************************************************************************/

#pragma once


//==============================================================================
class CompressorProcessor final : public juce::AudioProcessor
{
public:

    //==============================================================================
    // Constructor that lets you define input/output channels as well as parameters and their bounds
    CompressorProcessor()
        : juce::AudioProcessor (BusesProperties().withInput  ("Input",  juce::AudioChannelSet::stereo())
                                           .withOutput ("Output", juce::AudioChannelSet::stereo()))
    {
        // adding parameters as well as their bounds
	    addParameter (attack = new juce::AudioParameterFloat ({ "attack", 1 }, "Attack", 0.0f, 200.0f, 10.0f));
	    addParameter (release = new juce::AudioParameterFloat ({ "release", 1 }, "Release", 0.0f, 400.0f, 100.0f));
	    addParameter (threshold = new juce::AudioParameterFloat ({ "threshold", 1 }, "Threshold", -50.0f, 10.0f, -20.0f)); 
	    addParameter (ratio = new juce::AudioParameterFloat ({ "ratio", 1 }, "Ratio", 1.0f, 20.0f, 3.0f));
	    addParameter (thresMod = new juce::AudioParameterInt ({ "thresMod", 1 }, "Threshold Modulation Boolean", 0, 1, 0));
	    addParameter (thresModFreq = new juce::AudioParameterFloat ({ "thresModFreq", 1 }, "Threshold Modulation Freq", 1.0f, 20.0f, 2.0f));
    }

    //==============================================================================
    // This function is used before audio processing. It lets you initialize variables and set up any other resources prior to running the plugin
    void prepareToPlay (double samplerate, int samplesPerBlock) override 
    {
	    // initialize the processor and set initial parameter values
        juce::dsp::ProcessSpec spec { samplerate, static_cast<uint32_t>(samplesPerBlock), static_cast<uint32_t>(getTotalNumOutputChannels()) };
	    compressor.prepare(spec);
	    compressor.setAttack(10.0f);
	    compressor.setRelease(100.0f);
	    compressor.setThreshold(-20.0f);
	    compressor.setRatio(3.0f);
	    
	    lfo.initialise([](float x) { return std::sin(x); }, 256 );
	    rate = thresModFreq->get();
	    lfo.setFrequency(rate);
    }
    
    // This function is usually called after the plugin stops taking in audio. It can deallocate any memory used and clean out buffers
    void releaseResources() override {}

    // This is where all the audio processing happens. One block of audio input is handled at a time.
    void processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&) override
    {
        juce::dsp::AudioBlock<float> block (buffer);
	    juce::dsp::ProcessContextReplacing<float> context (block);
	
	    // read the values of the parameters in from the GUI
	    auto attackValue = attack->get();
	    auto releaseValue = release->get();
	    auto thresholdValue = threshold->get();
	    auto ratioValue = ratio->get();
	    auto thresModBool = thresMod->get();
	    auto freq = thresModFreq->get();
	    
	    lfo.setFrequency(freq);
	    float lfoDepth = 2.0f;
	    float lfoVal = (lfo.processSample(0.0f)+1.0f)*lfoDepth;
	    float modThres = juce::jmap(lfoVal, -1.0f, 1.0f, -50.0f, 5.0f)*lfoDepth;

	    // update parameters and apply them to the audio block with process()
	    compressor.setAttack(attackValue);
	    compressor.setRelease(releaseValue);
	    if(thresModBool) {
	        compressor.setThreshold(modThres);
	    }
	    else {
	        compressor.setThreshold(thresholdValue);
	    }
	    compressor.setRatio(ratioValue);
	    compressor.process(context);
    }

    //==============================================================================
    // This creates the GUI editor for the plugin
    juce::AudioProcessorEditor* createEditor() override          { return new juce::GenericAudioProcessorEditor (*this); }
    // We have a GUI editor for the plugin so we return true
    bool hasEditor() const override                        { return true;   }

    //==============================================================================
    const juce::String getName() const override            { return "Compressor PlugIn"; }
    bool acceptsMidi() const override                      { return false; }
    bool producesMidi() const override                     { return false; }
    double getTailLengthSeconds() const override           { return 0; }

    //==============================================================================
    // This returns the number of presets/configurations for the plugin. We only have a default configuration so we return 1
    int getNumPrograms() override                          { return 1; }
    // This returns the index of the currently selected program. This will always be 0 for this plugin
    int getCurrentProgram() override                       { return 0; }
    // This allows the user to switch to a different program if you have multiple
    void setCurrentProgram (int) override                  {}
    // This gives you the name of the program for a given index
    const juce::String getProgramName (int) override             { return "None"; }
    // This allows you to change the name of a program at the given index
    void changeProgramName (int, const juce::String&) override   {}

    //==============================================================================
    // This function saves the current state of each parameter to memory so that we can load the state of each parameter 
    // in the next session of running the pedal
    void getStateInformation (juce::MemoryBlock& destData) override
    {
	    juce::MemoryOutputStream (destData, true).writeFloat (*attack);
	    juce::MemoryOutputStream (destData, true).writeFloat (*release);
	    juce::MemoryOutputStream (destData, true).writeFloat (*threshold);
	    juce::MemoryOutputStream (destData, true).writeFloat (*ratio);
	    juce::MemoryOutputStream (destData, true).writeInt (*thresMod);
	    juce::MemoryOutputStream (destData, true).writeFloat (*thresModFreq);
    }

    // This function recalls the state of the parameters from the last session ran and restores it into the parameter
    void setStateInformation (const void* data, int sizeInBytes) override
    {
	    attack->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
	    release->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
	    threshold->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
	    ratio->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
	    thresMod->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readInt());
	    thresModFreq->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
    }

    //==============================================================================
    // This function checks to see if the requested input/output configuration is compatible with the coded plugin
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override
    {
        const auto& mainInLayout  = layouts.getChannelSet (true,  0);
        const auto& mainOutLayout = layouts.getChannelSet (false, 0);

        return (mainInLayout == mainOutLayout && (! mainInLayout.isDisabled()));
    }

private:
    //==============================================================================
    juce::dsp::Compressor<float> compressor;
    juce::dsp::Oscillator<float> lfo;
    
    juce::AudioParameterFloat* attack; //the attack time in milliseconds of the compressor
    juce::AudioParameterFloat* release; //the release time in milliseconds of the compressor
    juce::AudioParameterFloat* threshold; //the threshold in dB of the compressor
    juce::AudioParameterFloat* ratio; //the ratio of the compressor (must be higher or equal to 1)
    juce::AudioParameterInt* thresMod;
    juce::AudioParameterFloat* thresModFreq;
    
    juce::AudioParameterFloat* lfoRate;
    float rate;

    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (CompressorProcessor)
};
