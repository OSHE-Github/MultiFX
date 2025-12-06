/*
  ==============================================================================

   This file is part of the JUCE framework examples.
   Copyright (c) Raw Material Software Limited

   The code included in this file is provided under the terms of the ISC license
   http://www.isc.org/downloads/software-support-policy/isc-license. Permission
   to use, copy, modify, and/or distribute this software for any purpose with or
   without fee is hereby granted provided that the above copyright notice and
   this permission notice appear in all copies.

   THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
   REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
   AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
   INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
   LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
   OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
   PERFORMANCE OF THIS SOFTWARE.

  ==============================================================================
*/

/*******************************************************************************
 The block below describes the properties of this PIP. A PIP is a short snippet
 of code that can be read by the Projucer and used to generate a JUCE project.

 BEGIN_JUCE_PIP_METADATA

 name:             ReverbPlugin
 version:          1.0.0
 vendor:           JUCE
 website:          oshe.io
 description:      Reverb audio plugin.

 dependencies:     juce_audio_basics, juce_audio_devices, juce_audio_formats,
                   juce_audio_plugin_client, juce_audio_processors,
                   juce_audio_utils, juce_core, juce_data_structures, juce_dsp,
                   juce_events, juce_graphics, juce_gui_basics, juce_gui_extra
 exporter:         Linux Makefile

 moduleFlags:      JUCE_STRICT_REFCOUNTEDPOINTER=1

 type:             AudioProcessor
 mainClass:        ReverbProcessor

 useLocalCopy:     1

 END_JUCE_PIP_METADATA

*******************************************************************************/

#pragma once


//==============================================================================
class ReverbProcessor final : public juce::AudioProcessor
{
public:

    //==============================================================================
    ReverbProcessor()
        : juce::AudioProcessor (BusesProperties().withInput  ("Input",  juce::AudioChannelSet::stereo())
                                                 .withOutput ("Output", juce::AudioChannelSet::stereo()))
    {
        addParameter (roomSize = new juce::AudioParameterFloat ({ "roomSize", 1 }, "Room Size", 0.0f, 1.0f, 0.5f)); // 0 is small, 1 is large
        addParameter (damping = new juce::AudioParameterFloat ({"damping", 1}, "Damping", 0.0f, 1.0f, 0.5f)); // 0 is undamped, 1 is fully damped
        addParameter (wetLevel = new juce::AudioParameterFloat ({"wetLevel", 1}, "Wet Level", 0.0f, 1.0f, 0.5f));
        addParameter (dryLevel = new juce::AudioParameterFloat ({ "dryLevel", 1 }, "Dry Level", 0.0f, 1.0f, 0.5f));
        addParameter (width = new juce::AudioParameterFloat ({ "width", 1 }, "Width", 0.0f, 1.0f, 0.5f)); // 1 is very wide
        addParameter (freezeMode = new juce::AudioParameterFloat ({ "freezeMode", 1 }, "Freeze Mode", 0.0f, 1.0f, 0.0f)); // Enters freeze mode above 0.5
    }

    //==============================================================================
    void prepareToPlay (double sampleRate, int samplesPerBlock) override
    {   
        // Sets reverb parameters
        reverbParams.roomSize = roomSize->get();
        reverbParams.damping = damping->get();
        reverbParams.wetLevel = wetLevel->get();
        reverbParams.dryLevel = dryLevel->get();
        reverbParams.width = width->get();
        reverbParams.freezeMode = freezeMode->get();
        
        reverb.setParameters (reverbParams);
        reverb.setSampleRate (sampleRate);
    }
    
    void releaseResources() override {}

    void processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&) override
    {
        // Determines number of input channels for either mono or stereo processing
        totalNumInputChannels = getTotalNumInputChannels();
        
        if (totalNumInputChannels == 1)
        {
            reverb.processMono (buffer.getWritePointer(0), buffer.getNumSamples());
        }
        else
        {
            reverb.processStereo (buffer.getWritePointer(0), buffer.getWritePointer(1), buffer.getNumSamples());
        }
    }

    //==============================================================================
    juce::AudioProcessorEditor* createEditor() override         { return new juce::GenericAudioProcessorEditor (*this); }
    bool hasEditor() const override                             { return true;   }

    //==============================================================================
    const juce::String getName() const override                 { return "Reverb PlugIn"; }
    bool acceptsMidi() const override                           { return false; }
    bool producesMidi() const override                          { return false; }
    double getTailLengthSeconds() const override                { return 0; }

    //==============================================================================
    int getNumPrograms() override                               { return 1; }
    int getCurrentProgram() override                            { return 0; }
    void setCurrentProgram (int) override                       {}
    const juce::String getProgramName (int) override            { return "None"; }
    void changeProgramName (int, const juce::String&) override  {}

    //==============================================================================
    void getStateInformation (juce::MemoryBlock& destData) override
    {
        juce::MemoryOutputStream (destData, true).writeFloat (*roomSize);
        juce::MemoryOutputStream (destData, true).writeFloat (*damping);
        juce::MemoryOutputStream (destData, true).writeFloat (*wetLevel);
        juce::MemoryOutputStream (destData, true).writeFloat (*dryLevel);
        juce::MemoryOutputStream (destData, true).writeFloat (*width);
        juce::MemoryOutputStream (destData, true).writeFloat (*freezeMode);
    }

    void setStateInformation (const void* data, int sizeInBytes) override
    {
        roomSize->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        damping->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        wetLevel->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        dryLevel->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        width->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        freezeMode->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
    }

    //==============================================================================
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override
    {
        const auto& mainInLayout  = layouts.getChannelSet (true,  0);
        const auto& mainOutLayout = layouts.getChannelSet (false, 0);

        return (mainInLayout == mainOutLayout && (! mainInLayout.isDisabled()));
    }

private:
    //==============================================================================
    juce::Reverb reverb;
    juce::Reverb::Parameters reverbParams;
    
    juce::AudioParameterFloat* roomSize;
    juce::AudioParameterFloat* damping;
    juce::AudioParameterFloat* wetLevel;
    juce::AudioParameterFloat* dryLevel;
    juce::AudioParameterFloat* width;
    juce::AudioParameterFloat* freezeMode;
    
    int totalNumInputChannels;

    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (ReverbProcessor)
};