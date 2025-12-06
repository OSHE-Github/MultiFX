#include <JuceHeader.h>
//#include <juce_Oscillator.h>
#include "TremoloPluginV4.h" // Make sure to update this with current version!!

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new TremoloProcessor();
}


// Note: juce_dsp module added