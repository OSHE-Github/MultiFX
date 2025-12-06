#include <JuceHeader.h>
#include "TremoloPluginV5.h" // Make sure to update this with current version!!

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new TremoloProcessor();
}